from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain.tools.retriever import create_retriever_tool
import os

from ....settings import agents_settings


def load_and_split_markdown():
    """Loads a markdown file and splits it into sections based on headers."""
    print("\nЗагружаем markdown файл...")
    # Hardcoded path to the markdown file which needs to be refactored in the future
    file_path = "data/allsee-database/Команда AllSee.team.md"
    
    with open(file_path, "r", encoding="utf-8") as file:
        raw_text = file.read()

    # Split the text into sections based on headers. Need to make it configurable in the future
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "Header 1")], 
        strip_headers=False
    )

    split_docs = splitter.split_text(raw_text)

    # Filter out empty sections
    filtered_split_docs = []
    for split_id, split in enumerate(split_docs):
        if not split.metadata.get("Header 1", "").strip() and split.page_content.replace("#", "").replace("\n", "").strip() == "":
            print(f"Skip empty section {split_id} with no header and no content")
            continue
        filtered_split_docs.append(split)

    print(f"Number of sections: {len(filtered_split_docs)}")
    print("\nSection preview:")
    for i, doc in enumerate(filtered_split_docs):
        print(f"\nSection {i+1}:")
        print(f"Header: {doc.metadata.get('Header 1', 'No header')}")
        print(f"Content: {doc.page_content[:100]}...")
    
    return filtered_split_docs


# Hardcoded path to the Chroma database directory. Need to make it configurable in the future
chroma_dir = "data/rag-chroma"
# Check if the Chroma database directory exists and contains a valid database
has_existing_db = (
    os.path.exists(chroma_dir) and 
    os.path.exists(os.path.join(chroma_dir, "chroma.sqlite3"))
)

# If the database exists, load it; otherwise, create a new one
if has_existing_db:
    print("\nFound existing Chroma database, loading...")
    vectorstore = Chroma(
        persist_directory=chroma_dir,
        collection_name="rag-chroma",
        embedding_function=OpenAIEmbeddings(api_key=agents_settings.openai_api_key),
    )
    doc_count = vectorstore._collection.count()
    print(f"Loaded vectorstore with {doc_count} documents")
    
    if doc_count == 0:
        print("Existing database is empty, processing markdown and creating new...")
        split_docs = load_and_split_markdown()
        # Create a new vectorstore with the loaded documents. For now, we are using OpenAIEmbeddings, but it can be made more configurable in the future
        vectorstore = Chroma.from_documents(
            documents=split_docs,
            collection_name="rag-chroma",
            persist_directory=chroma_dir,
            embedding=OpenAIEmbeddings(api_key=agents_settings.openai_api_key),
        )
        print(f"Created new vectorstore with {vectorstore._collection.count()} documents")
else:
    print("\nNo existing Chroma database found, processing markdown and creating new...")
    split_docs = load_and_split_markdown()
    vectorstore = Chroma.from_documents(
        documents=split_docs,
        collection_name="rag-chroma",
        persist_directory=chroma_dir,
        embedding=OpenAIEmbeddings(api_key=agents_settings.openai_api_key),
    )
    print(f"Created new vectorstore with {vectorstore._collection.count()} documents")

# Create a retriever from the vectorstore. Params also hardcoded for now
retriever = vectorstore.as_retriever(search_kwargs={'k': 3})
print(f"\nCreated new retriever with search_kwargs: {retriever.search_kwargs}")

# Create a retriever tool with the retriever
retrieval_tool = create_retriever_tool(
    retriever=retriever,
    name="AllSeeTeamInfoRetriever",
    description=(
        """
        Найти релевантную информацию о компании AllSee.team по запросу. 
        Для запроса сформулируй максимально развёрнутый вопрос, 
        содержащий точное название раздела из базы знаний и все детали запрашиваемой информации.
        В данной базе содержаться следующая информация:
        - Почему мы?
        - Кто мы?
        - Наша миссия
        - Профиль компании
        - Философия
        - Ценности
        - Легенда и история
        - Сферы деятельности, с которыми мы работаем
        - Портреты потребителей
        - Этапы принятия решения о работе с нами
        - Наши услуги
        - Преимущества и результаты от внедрения ИИ
        - Преимущества решений для наших сфер
        """
    ),
)