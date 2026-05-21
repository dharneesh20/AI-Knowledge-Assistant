from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import Document, QueryLog, DocumentChunk
from .forms import RegisterForm, DocumentUploadForm

from core.services.text_extract import extract_text_from_upload
from core.services.chunking import chunk_text
from core.services.embeddings import embed_query, embed_texts
from core.services.vector_store import (
    add_chunks_to_index,
    search,
    rebuild_user_index,
)
from core.services.groq_llm import groq_answer


# -----------------------------
# HELPERS
# -----------------------------
def _querylog_field_names():
    return [f.name for f in QueryLog._meta.fields]


def _querylog_user_field():
    fields = _querylog_field_names()
    if "user" in fields:
        return "user"
    if "owner" in fields:
        return "owner"
    if "created_by" in fields:
        return "created_by"
    return None


def _querylog_response_field():
    fields = _querylog_field_names()
    if "response" in fields:
        return "response"
    if "answer" in fields:
        return "answer"
    if "result" in fields:
        return "result"
    if "output" in fields:
        return "output"
    return None


def _save_querylog(request, query, answer):
    try:
        data = {"query": query}
        ufield = _querylog_user_field()
        rfield = _querylog_response_field()

        if ufield:
            data[ufield] = request.user
        if rfield:
            data[rfield] = answer

        QueryLog.objects.create(**data)
    except Exception:
        pass


# -----------------------------
# LANDING
# -----------------------------
def landing(request):
    return render(request, "landing.html")


# -----------------------------
# AUTH
# -----------------------------
def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = RegisterForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully. Please login.")
            return redirect("login")
        messages.error(request, "Registration failed. Please check the form.")

    return render(request, "auth/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "auth/login.html")


def logout_view(request):
    logout(request)
    return redirect("landing")


# -----------------------------
# DASHBOARD
# -----------------------------
@login_required
def dashboard(request):
    docs = Document.objects.filter(owner=request.user).order_by("-created_at")[:6]
    total_docs = Document.objects.filter(owner=request.user).count()
    indexed_docs = Document.objects.filter(owner=request.user, is_indexed=True).count()
    logs = _get_user_logs_queryset(request)[:6]
    return render(
        request,
        "dashboard.html",
        {
            "docs": docs,
            "total_docs": total_docs,
            "indexed_docs": indexed_docs,
            "logs": logs,
        },
    )


# -----------------------------
# DOCUMENTS
# -----------------------------
@login_required
def documents(request):
    docs = Document.objects.filter(owner=request.user).order_by("-created_at")
    form = DocumentUploadForm()
    return render(request, "documents.html", {"docs": docs, "form": form})


@login_required
def document_upload(request):
    if request.method != "POST":
        return redirect("documents")

    form = DocumentUploadForm(request.POST, request.FILES)

    if not form.is_valid():
        messages.error(request, "Upload failed. Please select a valid file.")
        return redirect("documents")

    doc = form.save(commit=False)
    doc.owner = request.user
    doc.save()

    try:
        raw_text = extract_text_from_upload(doc.file.path)
        chunks = chunk_text(raw_text)

        if not chunks:
            messages.error(request, "No readable text found in this document.")
            return redirect("documents")

        # delete old chunks
        DocumentChunk.objects.filter(document=doc).delete()

        chunk_meta = []
        for i, c in enumerate(chunks):
            chunk_obj = DocumentChunk.objects.create(
                document=doc,
                content=c,
                chunk_index=i,
            )

            chunk_meta.append(
                {
                    "chunk_id": chunk_obj.id,
                    "document_id": doc.id,
                    "owner_id": request.user.id,
                    "text": c,
                    "chunk_index": i,
                    "document_title": doc.title,
                }
            )

        embeddings = embed_texts(chunks)
        add_chunks_to_index(chunk_meta, embeddings)

        doc.is_indexed = True
        doc.save()

        messages.success(request, "Document uploaded & indexed successfully!")

    except Exception as e:
        messages.error(request, f"Indexing failed: {str(e)}")

    return redirect("documents")

@login_required 
def document_detail(request, pk): 
    doc = get_object_or_404(Document, pk=pk, owner=request.user)
    return render(request, "document_detail.html", {"doc": doc})



@login_required
def document_delete(request, pk):
    doc = get_object_or_404(Document, pk=pk, owner=request.user)

    if request.method == "POST":
        doc.delete()
        messages.success(request, "Document deleted successfully.")
        return redirect("documents")

    return render(request, "document_detail.html", {"doc": doc})


@login_required
def document_reindex(request):
    """
    Clears FAISS and rebuilds from DB for THIS USER.
    """
    if request.method != "POST":
        return redirect("documents")

    # clear global faiss
    rebuild_user_index()

    docs = Document.objects.filter(owner=request.user).order_by("-created_at")

    success = 0
    failed = 0

    for doc in docs:
        try:
            raw_text = extract_text_from_upload(doc.file.path)
            chunks = chunk_text(raw_text)

            if not chunks:
                failed += 1
                continue

            DocumentChunk.objects.filter(document=doc).delete()

            chunk_meta = []
            for i, c in enumerate(chunks):
                chunk_obj = DocumentChunk.objects.create(
                    document=doc,
                    content=c,
                    chunk_index=i,
                )
                chunk_meta.append(
                    {
                        "chunk_id": chunk_obj.id,
                        "document_id": doc.id,
                        "owner_id": request.user.id,
                        "text": c,
                        "chunk_index": i,
                        "document_title": doc.title,
                    }
                )

            embeddings = embed_texts(chunks)
            add_chunks_to_index(chunk_meta, embeddings)

            doc.is_indexed = True
            doc.save()
            success += 1

        except Exception:
            failed += 1

    messages.success(request, f"Index rebuilt. Success: {success}, Failed: {failed}")
    return redirect("documents")


# -----------------------------
# CHAT (GROQ + FAISS)
# -----------------------------
@login_required
def chat(request):
    answer = None
    hits = []
    query = ""

    if request.method == "POST":
        query = request.POST.get("query", "").strip()

        if not query:
            messages.error(request, "Please type a question.")
            return redirect("chat")

        try:
            qvec = embed_query(query)
            hits = search(request.user.id, qvec, top_k=5)
        except Exception:
            hits = []

        if hits:
            context = "\n\n".join([h["text"] for h in hits])
            answer = groq_answer(query, context)
        else:
            answer = "No relevant information found in your documents."

        _save_querylog(request, query, answer)

    return render(
        request,
        "chat.html",
        {"query": query, "answer": answer, "hits": hits},
    )

# ----------------------------- # LOGS # ----------------------------- 
def _get_user_logs_queryset(request):
    """
    Returns logs filtered for logged-in user safely.
    Works even if QueryLog has different field names.
    """
    try:
        fields = [f.name for f in QueryLog._meta.fields]

        # detect user field
        if "user" in fields:
            ufield = "user"
        elif "owner" in fields:
            ufield = "owner"
        elif "created_by" in fields:
            ufield = "created_by"
        else:
            ufield = None

        # detect created time field
        if "created_at" in fields:
            cfield = "created_at"
        elif "timestamp" in fields:
            cfield = "timestamp"
        elif "created_on" in fields:
            cfield = "created_on"
        else:
            cfield = None

        qs = QueryLog.objects.all()

        if ufield:
            qs = qs.filter(**{ufield: request.user})

        if cfield:
            qs = qs.order_by(f"-{cfield}")
        else:
            qs = qs.order_by("-id")

        return qs

    except Exception:
        return QueryLog.objects.none()

@login_required
def logs(request):
    logs = _get_user_logs_queryset(request)
    return render(request, "logs.html", {"logs": logs})

@login_required
def clear_logs(request):
    if request.method == "POST":
        try:
            fields = [f.name for f in QueryLog._meta.fields]

            if "user" in fields:
                QueryLog.objects.filter(user=request.user).delete()
            elif "owner" in fields:
                QueryLog.objects.filter(owner=request.user).delete()
            elif "created_by" in fields:
                QueryLog.objects.filter(created_by=request.user).delete()
            else:
                QueryLog.objects.all().delete()

            messages.success(request, "Logs cleared successfully.")
        except Exception:
            messages.error(request, "Failed to clear logs.")

    return redirect("logs")
