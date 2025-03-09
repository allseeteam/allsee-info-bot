from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain.tools.retriever import create_retriever_tool
import os

from ....settings import agents_settings


def load_and_split_markdown():
    """Загрузка и разбиение markdown файла на документы."""
    print("\nЗагружаем markdown файл...")
    file_path = "data/allsee-database/Команда AllSee.team.md"
    
    with open(file_path, "r", encoding="utf-8") as file:
        raw_text = file.read()

    # Разбиваем текст на части по заголовкам
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "Header 1")], 
        strip_headers=False
    )

    split_docs = splitter.split_text(raw_text)

    # Фильтруем пустые разделы
    filtered_split_docs = []
    for split_id, split in enumerate(split_docs):
        if not split.metadata.get("Header 1", "").strip() and split.page_content.replace("#", "").replace("\n", "").strip() == "":
            print(f"Раздел {split_id} пустой и будет пропущен.")
            continue
        filtered_split_docs.append(split)

    print(f"Количество разделов: {len(filtered_split_docs)}")
    print("\nРазделы документа:")
    for i, doc in enumerate(filtered_split_docs):
        print(f"\nРаздел {i+1}:")
        print(f"Заголовок: {doc.metadata.get('Header 1', 'Без заголовка')}")
        print(f"Предпросмотр содержимого: {doc.page_content[:100]}...")
    
    return filtered_split_docs


# Проверяем существование и содержимое директории Chroma
chroma_dir = "data/rag-chroma"
has_existing_db = (
    os.path.exists(chroma_dir) and 
    os.path.exists(os.path.join(chroma_dir, "chroma.sqlite3"))
)

if has_existing_db:
    print("\nНайдена существующая база данных Chroma, загружаем...")
    vectorstore = Chroma(
        persist_directory=chroma_dir,
        collection_name="rag-chroma",
        embedding_function=OpenAIEmbeddings(api_key=agents_settings.openai_api_key),
    )
    doc_count = vectorstore._collection.count()
    print(f"Загружено векторное хранилище с {doc_count} документами")
    
    if doc_count == 0:
        print("Существующая база данных пуста, обрабатываем markdown и создаем новое векторное хранилище...")
        split_docs = load_and_split_markdown()
        vectorstore = Chroma.from_documents(
            documents=split_docs,
            collection_name="rag-chroma",
            persist_directory=chroma_dir,
            embedding=OpenAIEmbeddings(api_key=agents_settings.openai_api_key),
        )
        print(f"Создано новое векторное хранилище с {vectorstore._collection.count()} документами")
else:
    print("\nБаза данных Chroma не найдена, обрабатываем markdown и создаем новую...")
    split_docs = load_and_split_markdown()
    vectorstore = Chroma.from_documents(
        documents=split_docs,
        collection_name="rag-chroma",
        persist_directory=chroma_dir,
        embedding=OpenAIEmbeddings(api_key=agents_settings.openai_api_key),
    )
    print(f"Создано новое векторное хранилище с {vectorstore._collection.count()} документами")

# Создаем ретривер для векторного хранилища
retriever = vectorstore.as_retriever(search_kwargs={'k': 3})
print(f"\nРетривер настроен с параметрами поиска: {retriever.search_kwargs}")

# Создаем tool для ретривера
retrieval_tool = create_retriever_tool(
    retriever=retriever,
    name="AllSeeTeamInfoRetriever",
    description=(
        """
        Найти релевантную информацию о компании AllSee.team по запросу. 
        Для запроса сформулируй максимально развёнутый вопрос, 
        содержащий точное название раздела из базы знаний и все детали запрашиваемой информации.
        В данной базе содержиться следующая информация:
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