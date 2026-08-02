"""
Technology Registry for CurricuAlign AI Technology Normalization Engine.

Holds the canonical catalog of technologies and their aliases. Provides
single-source-of-truth lookup for alias resolution and category assignment,
plus support for loading external alias files and category overrides.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from backend.industry_engine.processing.normalization.config import NormalizationConfig
from backend.industry_engine.processing.normalization.exceptions import (
    DuplicateCanonicalIdError,
    EmptyTechnologyNameError,
    InvalidAliasError,
    TechnologyNotRegisteredError,
)
from backend.industry_engine.processing.normalization.models import CATEGORY_DISPLAY
from backend.industry_engine.processing.normalization.normalizer import TechnologyNormalizer

logger = logging.getLogger("industry_engine.processing.normalization.technology_registry")


class TechnologyEntry:
    """
    Lightweight in-memory entry for a registered canonical technology.
    """

    __slots__ = ("id", "canonical_name", "category", "aliases")

    def __init__(self, id: str, canonical_name: str, category: str, aliases: Optional[List[str]] = None):
        self.id = id
        self.canonical_name = canonical_name
        self.category = category
        self.aliases = list(aliases or [])

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "canonical_name": self.canonical_name,
            "category": self.category,
            "aliases": list(self.aliases),
        }


# ------------------------------------------------------------------
# Builtin catalog organized by LLM extraction category key.
# Each entry is (canonical_name, [aliases...]).
# ------------------------------------------------------------------
BUILTIN_TECHNOLOGIES: Dict[str, List[tuple]] = {
    "languages": [
        ("Python", ["py", "python3"]),
        ("JavaScript", ["JS", "js", "ECMAScript", "es6"]),
        ("TypeScript", ["TS", "ts"]),
        ("Java", []),
        ("C", ["c language", "ansi c"]),
        ("C++", ["cpp", "c plus plus"]),
        ("C#", ["csharp", "c sharp"]),
        ("Go", ["Golang", "go lang"]),
        ("Rust", ["rust-lang"]),
        ("Ruby", []),
        ("PHP", ["php7", "php8"]),
        ("Swift", []),
        ("Kotlin", []),
        ("Scala", []),
        ("R", ["r language", "r programming"]),
        ("SQL", ["structured query language"]),
        ("Dart", []),
        ("Perl", []),
        ("Haskell", []),
        ("Elixir", []),
        ("MATLAB", ["matlab", "mat lab"]),
        ("Assembly", ["asm"]),
        ("Objective-C", ["objective c", "obj-c"]),
        ("Shell", ["Bash", "bash scripting", "shell scripting", "sh"]),
        ("PowerShell", ["powershell scripting", "ps"]),
        ("Groovy", []),
        ("Lua", []),
        ("Visual Basic", ["VB", "vb.net", "visual basic .net"]),
    ],
    "frameworks": [
        ("React", ["React.js", "ReactJS", "react js"]),
        ("Angular", ["AngularJS", "Angular 2", "Angular 2+"]),
        ("Vue", ["Vue.js", "VueJS", "vue js"]),
        ("Django", []),
        ("Flask", []),
        ("FastAPI", ["Fast API", "fast-api", "FastApi"]),
        ("Spring Boot", ["Springboot", "spring-boot", "spring boot framework"]),
        ("Spring", ["spring framework"]),
        ("Node.js", ["NodeJS", "node js", "node"]),
        ("Express", ["Express.js", "expressjs", "express js"]),
        (".NET", ["dotnet", ".net framework", "dot net"]),
        ("ASP.NET", ["asp net", "aspnet", "asp.net core"]),
        ("Ruby on Rails", ["Rails", "rails"]),
        ("Laravel", []),
        ("Symfony", []),
        ("Next.js", ["NextJS", "next js", "nextjs"]),
        ("Nuxt.js", ["Nuxt", "nuxtjs"]),
        ("Svelte", []),
        ("jQuery", ["jquery"]),
        ("Bootstrap", ["bootstrap css"]),
        ("Tailwind CSS", ["tailwind", "tailwindcss"]),
        ("Hibernate", []),
        ("MyBatis", []),
        ("GraphQL", ["graphql api", "apollo"]),
        ("gRPC", ["grpc framework"]),
        ("WebSockets", ["websocket"]),
        ("React Native", ["reactnative", "react-native"]),
        ("Flutter", ["flutter framework"]),
    ],
    "libraries": [
        ("Pandas", ["pandas library"]),
        ("NumPy", ["numpy", "np"]),
        ("Scikit-learn", ["sklearn", "scikit learn", "scikit-learning"]),
        ("Matplotlib", ["matplotlib"]),
        ("Seaborn", []),
        ("TensorFlow", ["tensorflow", "TF"]),
        ("PyTorch", ["pytorch", "torch"]),
        ("Keras", []),
        ("OpenCV", ["opencv"]),
        ("NLTK", ["nltk library"]),
        ("spaCy", ["spacy", "spacy nlp"]),
        ("Requests", ["python requests"]),
        ("SQLAlchemy", ["sqlalchemy orm"]),
        ("Pydantic", ["pydantic models"]),
        ("BeautifulSoup", ["beautiful soup", "bs4"]),
        ("XGBoost", ["xgboost"]),
        ("LightGBM", ["lightgbm"]),
        ("Transformers", ["huggingface transformers", "hf transformers"]),
        ("Celery", ["celery task queue"]),
    ],
    "databases": [
        ("PostgreSQL", ["Postgres", "postgresql", "psql"]),
        ("MySQL", ["mysql", "my sql"]),
        ("SQLite", ["sqlite3"]),
        ("MongoDB", ["Mongo", "mongodb", "mongo db"]),
        ("Redis", ["redis cache", "redis-cache", "redis db"]),
        ("Cassandra", ["apache cassandra"]),
        ("DynamoDB", ["amazon dynamodb", "aws dynamodb"]),
        ("Oracle", ["oracle database", "oracle db"]),
        ("SQL Server", ["MSSQL", "ms sql server", "microsoft sql server"]),
        ("MariaDB", ["mariadb"]),
        ("Elasticsearch", ["elastic search", "ES", "elasticsearch"]),
        ("Neo4j", ["neo4j graph"]),
        ("InfluxDB", ["influx db", "influx"]),
        ("CouchDB", ["couch db"]),
        ("ClickHouse", ["click house"]),
        ("Firestore", ["google firestore", "cloud firestore"]),
        ("Supabase", ["supabase db"]),
        ("Hive", ["apache hive"]),
        ("HBase", ["apache hbase"]),
    ],
    "vector_databases": [
        ("ChromaDB", ["Chroma", "chromadb", "chroma db"]),
        ("Pinecone", ["pinecone"]),
        ("Qdrant", ["qdrant"]),
        ("Weaviate", ["weaviate"]),
        ("Milvus", ["milvus"]),
        ("FAISS", ["faiss", "facebook faiss"]),
        ("LanceDB", ["lance db", "lancedb"]),
        ("Redis Vector Store", ["redis vector database"]),
    ],
    "cloud": [
        ("AWS", ["Amazon Web Services", "amazon aws", "aws cloud"]),
        ("GCP", ["Google Cloud Platform", "google cloud", "google cloud platform"]),
        ("Azure", ["Microsoft Azure", "azure cloud", "ms azure"]),
        ("Heroku", []),
        ("Cloudflare", ["cloudflare workers"]),
        ("DigitalOcean", ["digital ocean", "do"]),
        ("IBM Cloud", ["ibm cloud"]),
        ("Alibaba Cloud", ["alibaba cloud"]),
        ("Vercel", ["vercel"]),
        ("Netlify", ["netlify"]),
        ("Firebase", ["google firebase", "firebase"]),
        ("Oracle Cloud", ["oracle cloud infrastructure", "oci"]),
        ("Cloud Foundry", ["cloudfoundry"]),
    ],
    "devops": [
        ("Docker", ["docker", "docker container"]),
        ("Kubernetes", ["K8s", "k8s", "kube", "k8", "kubernetes"]),
        ("Jenkins", ["jenkins ci"]),
        ("GitHub Actions", ["github actions", "gh actions", "actions"]),
        ("GitLab CI/CD", ["gitlab ci", "gitlab cicd"]),
        ("CircleCI", ["circle ci", "circleci"]),
        ("Travis CI", ["travis", "travisci"]),
        ("TeamCity", ["teamcity"]),
        ("Bamboo", ["atlassian bamboo"]),
        ("Azure DevOps", ["azure devops pipelines", "azure pipelines"]),
        ("Buildkite", ["buildkite"]),
        ("ArgoCD", ["argo cd", "argocd"]),
        ("Consul", ["hashicorp consul"]),
        ("Vault", ["hashicorp vault"]),
        ("Helm", ["helm charts"]),
        ("Nagios", []),
        ("PagerDuty", ["pagerduty"]),
        ("SonarQube", ["sonarqube", "sonar qube"]),
    ],
    "ai": [
        ("Machine Learning", ["ML", "ml", "machine-learning", "M/L", "ml engineering"]),
        ("Deep Learning", ["DL", "deeplearning", "deep-learning"]),
        ("Artificial Intelligence", ["AI", "ai", "artificial intelligence"]),
        ("Artificial Intelligence & Machine Learning", ["AI/ML", "ai/ml", "ai-ml", "AI & ML", "ai & ml"]),
        ("Generative AI", ["GenAI", "Gen AI", "gen ai", "genai", "generative ai"]),
        ("Large Language Models", ["LLMs", "LLM", "llms", "llm", "large language model"]),
        ("Computer Vision", ["CV", "computer-vision", "cv"]),
        ("Natural Language Processing", ["NLP", "nlp", "natural-language-processing"]),
        ("Reinforcement Learning", ["RL", "reinforcement-learning"]),
        ("Data Science", ["data-science", "data science"]),
        ("MLOps", ["ml-ops", "mlops"]),
        ("RAG", ["Retrieval Augmented Generation", "retrieval-augmented-generation", "rag pipeline"]),
        ("Agentic AI", ["agentic-ai", "agentic ai"]),
        ("Prompt Engineering", ["prompt-engineering", "prompt engineering"]),
        ("Fine-tuning", ["fine tuning", "fine-tune", "llm fine tuning"]),
    ],
    "llm_frameworks": [
        ("LangChain", ["langchain", "lang chain"]),
        ("LlamaIndex", ["llamaindex", "llama index"]),
        ("vLLM", ["vllm", "vllm inference"]),
        ("Haystack", ["haystack framework"]),
        ("Semantic Kernel", ["semantic-kernel", "microsoft semantic kernel"]),
        ("DSPy", ["dspy"]),
        ("OpenAI SDK", ["openai python sdk", "openai api"]),
        ("Anthropic SDK", ["anthropic api", "claude api"]),
        ("LiteLLM", ["litellm"]),
        ("LangSmith", ["langsmith"]),
    ],
    "agent_frameworks": [
        ("CrewAI", ["Crew AI", "crew ai", "crewai"]),
        ("AutoGen", ["Microsoft AutoGen", "microsoft autogen", "autogen"]),
        ("LangGraph", ["langgraph", "lang graph"]),
        ("LangSmith", ["langsmith"]),
        ("OpenAI Agents SDK", ["openai agents", "agents sdk"]),
        ("Pydantic AI", ["pydantic-ai", "pydantic ai"]),
    ],
    "operating_systems": [
        ("Linux", ["linux os", "gnu/linux"]),
        ("Ubuntu", ["ubuntu os"]),
        ("CentOS", ["centos os"]),
        ("Red Hat", ["RedHat", "redhat", "rhel"]),
        ("Debian", ["debian os"]),
        ("Windows", ["windows os", "windows server"]),
        ("macOS", ["Mac OS", "mac os", "osx"]),
        ("iOS", ["ios development"]),
        ("Android", ["android os"]),
    ],
    "developer_tools": [
        ("VS Code", ["Visual Studio Code", "vscode", "visual studio code"]),
        ("Postman", ["postman api", "postman"]),
        ("Webpack", ["webpack"]),
        ("Vite", ["vite"]),
        ("Babel", ["babel js"]),
        ("ESLint", ["eslint"]),
        ("Prettier", ["prettier"]),
        ("Jupyter", ["Jupyter Notebook", "jupyter notebook", "jupyterlab", "jupyter lab"]),
        ("IntelliJ IDEA", ["intellij", "idea"]),
        ("PyCharm", ["pycharm"]),
        ("Eclipse", ["eclipse ide"]),
        ("Visual Studio", ["visual studio ide", "vs"]),
        ("Swagger", ["swagger ui", "openapi"]),
    ],
    "version_control": [
        ("Git", ["git vcs"]),
        ("GitHub", ["github"]),
        ("GitLab", ["gitlab"]),
        ("Bitbucket", ["bitbucket"]),
        ("SVN", ["Subversion", "subversion", "apache subversion"]),
        ("Mercurial", ["mercurial"]),
        ("Azure Repos", ["azure repos", "azure devops repos"]),
    ],
    "message_brokers": [
        ("Apache Kafka", ["Kafka", "kafka", "kafka broker", "apache kafka"]),
        ("RabbitMQ", ["rabbitmq", "rabbit mq"]),
        ("ActiveMQ", ["apache activemq"]),
        ("Amazon SQS", ["SQS", "sqs", "aws sqs"]),
        ("Google Pub/Sub", ["gcp pub sub", "pubsub", "google pubsub"]),
        ("ZeroMQ", ["zeromq", "0mq"]),
        ("Apache Pulsar", ["pulsar", "pulsar messaging"]),
        ("NATS", ["nats messaging"]),
    ],
    "container_technologies": [
        ("Podman", ["podman"]),
        ("Containerd", ["containerd"]),
        ("CRI-O", ["cri o", "crio"]),
        ("Docker Compose", ["docker-compose", "docker compose"]),
        ("OpenShift", ["red hat openshift", "openshift container platform"]),
    ],
    "infrastructure_tools": [
        ("Terraform", ["terraform", "hashicorp terraform"]),
        ("Ansible", ["ansible"]),
        ("Pulumi", ["pulumi"]),
        ("CloudFormation", ["AWS CloudFormation", "aws cloudformation", "cloud formation"]),
        ("Vagrant", ["vagrant"]),
        ("Packer", ["hashicorp packer"]),
        ("Chef", ["chef automation"]),
        ("Puppet", ["puppet"]),
        ("SaltStack", ["salt stack", "saltstack"]),
    ],
    "monitoring_tools": [
        ("Prometheus", ["prometheus metrics"]),
        ("Grafana", ["grafana"]),
        ("Datadog", ["datadog"]),
        ("New Relic", ["newrelic", "new relic"]),
        ("Splunk", ["splunk"]),
        ("Kibana", ["kibana"]),
        ("Sentry", ["sentry"]),
        ("ELK Stack", ["Elastic Stack", "elastic stack", "elk"]),
        ("OpenTelemetry", ["opentelemetry", "otel"]),
        ("CloudWatch", ["AWS CloudWatch", "aws cloudwatch", "amazon cloudwatch"]),
        ("Zabbix", ["zabbix"]),
        ("Loki", ["grafana loki"]),
    ],
    "testing_frameworks": [
        ("PyTest", ["pytest", "Pytest"]),
        ("JUnit", ["junit", "junit 5"]),
        ("Jest", ["jest"]),
        ("Cypress", ["cypress"]),
        ("Selenium", ["selenium"]),
        ("Playwright", ["playwright"]),
        ("Mocha", ["mocha js"]),
        ("TestNG", ["testng"]),
        ("Cucumber", ["cucumber"]),
        ("NUnit", ["nunit"]),
        ("xUnit", ["xunit", "xunit.net"]),
        ("Vitest", ["vitest"]),
        ("Mockito", ["mockito"]),
    ],
}


class TechnologyRegistry:
    """
    Canonical registry of technologies, their categories, and aliases.

    Provides:
      - register() for adding canonical technologies.
      - resolve() for mapping raw values to canonical names.
      - get_entry() / get_category() for category assignment.
      - External alias file + category override loading.
    """

    def __init__(self, config: Optional[NormalizationConfig] = None):
        self._config = config or NormalizationConfig()
        self._normalizer = TechnologyNormalizer()
        self._entries: Dict[str, TechnologyEntry] = {}
        self._ids: Dict[str, str] = {}
        self._alias_map: Dict[str, str] = {}
        self._fuzzy_map: Dict[str, str] = {}

        self._load_builtin()
        self._load_category_overrides(self._config.categories)
        if self._config.alias_file:
            self._load_alias_file(self._config.alias_file)

        logger.info(
            f"[TechnologyRegistry] Loaded {len(self._entries)} canonical technologies, "
            f"{len(self._alias_map)} alias mappings."
        )

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------
    def register(
        self,
        canonical_name: str,
        category: str,
        aliases: Optional[List[str]] = None,
        explicit_id: Optional[str] = None,
    ) -> TechnologyEntry:
        """
        Register a canonical technology with its category and aliases.

        Raises:
            EmptyTechnologyNameError: If the canonical name is blank.
            InvalidAliasError: If an alias is blank/malformed.
            DuplicateCanonicalIdError: If the canonical ID is already registered.
        """
        name = canonical_name.strip()
        if not name:
            raise EmptyTechnologyNameError("Canonical technology name must be non-empty.")

        cat = (category or "").strip() or "Unknown"
        for alias in (aliases or []):
            if not isinstance(alias, str) or not alias.strip():
                raise InvalidAliasError(f"Alias for '{name}' must be a non-empty string.")
        aliases = [a.strip() for a in (aliases or [])]

        entry_id = self._normalizer.canonical_id(name, explicit_id)
        if entry_id in self._ids:
            existing = self._entries[self._ids[entry_id]].canonical_name
            if existing != name:
                raise DuplicateCanonicalIdError(
                    f"Canonical ID '{entry_id}' already registered for '{existing}'; cannot register '{name}'."
                )
            return self._entries[self._ids[entry_id]]

        entry = TechnologyEntry(id=entry_id, canonical_name=name, category=cat, aliases=aliases)
        self._entries[name] = entry
        self._ids[entry_id] = name

        self._index(name, name)
        for alias in aliases:
            self._index(name, alias)

        logger.debug(f"[TechnologyRegistry] Registered '{name}' (category='{cat}', id='{entry_id}').")
        return entry

    def register_alias(self, canonical_name: str, alias: str) -> None:
        """
        Attach an additional alias to an already registered technology.
        """
        if canonical_name not in self._entries:
            raise TechnologyNotRegisteredError(
                f"Cannot add alias '{alias}': technology '{canonical_name}' is not registered."
            )
        alias = alias.strip()
        if not alias:
            raise InvalidAliasError("Alias must be non-empty.")
        self._entries[canonical_name].aliases.append(alias)
        self._index(canonical_name, alias)

    def _index(self, canonical_name: str, alias: str) -> None:
        soft_key = self._normalizer.normalize_key_soft(alias)
        fuzzy_key = self._normalizer.normalize_key_aggressive(alias)

        if soft_key in self._alias_map and self._alias_map[soft_key] != canonical_name:
            logger.warning(
                f"[TechnologyRegistry] Alias collision on soft key '{soft_key}': "
                f"'{self._alias_map[soft_key]}' vs '{canonical_name}' (first wins)."
            )
        else:
            self._alias_map[soft_key] = canonical_name

        if fuzzy_key in self._fuzzy_map and self._fuzzy_map[fuzzy_key] != canonical_name:
            logger.warning(
                f"[TechnologyRegistry] Alias collision on fuzzy key '{fuzzy_key}': "
                f"'{self._fuzzy_map[fuzzy_key]}' vs '{canonical_name}' (first wins)."
            )
        else:
            self._fuzzy_map[fuzzy_key] = canonical_name

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------
    def resolve(self, value: str) -> Optional[str]:
        """
        Map a raw technology value to its canonical name, or None if unknown.
        """
        if not isinstance(value, str):
            return None
        value = value.strip()
        if not value:
            return None

        soft_key = self._normalizer.normalize_key_soft(value)
        if soft_key in self._alias_map:
            return self._alias_map[soft_key]

        fuzzy_key = self._normalizer.normalize_key_aggressive(value)
        if fuzzy_key in self._fuzzy_map:
            return self._fuzzy_map[fuzzy_key]

        return None

    def is_known(self, value: str) -> bool:
        """Return True if the value resolves to a registered technology."""
        return self.resolve(value) is not None

    def get_entry(self, canonical_name: str) -> Optional[TechnologyEntry]:
        """Return the entry for a canonical name, or None."""
        return self._entries.get(canonical_name)

    def get_entry_by_id(self, entry_id: str) -> Optional[TechnologyEntry]:
        """Return the entry for a canonical ID, or None."""
        name = self._ids.get(entry_id)
        return self._entries.get(name) if name else None

    def get_category(self, canonical_name: str) -> Optional[str]:
        """Return the category label for a canonical name, or None."""
        entry = self._entries.get(canonical_name)
        return entry.category if entry else None

    def entries(self) -> List[TechnologyEntry]:
        """Return all registered entries."""
        return list(self._entries.values())

    def __len__(self) -> int:
        return len(self._entries)

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------
    def _load_builtin(self) -> None:
        for category_key, techs in BUILTIN_TECHNOLOGIES.items():
            display_category = CATEGORY_DISPLAY.get(category_key, "Unknown")
            for canonical_name, aliases in techs:
                self.register(canonical_name, display_category, aliases)

    def _load_category_overrides(self, overrides: Dict[str, str]) -> None:
        for tech, category in overrides.items():
            if tech in self._entries:
                self._entries[tech].category = category
                logger.debug(f"[TechnologyRegistry] Category override: '{tech}' -> '{category}'.")
            else:
                self.register(tech, category)

    def _load_alias_file(self, alias_file: str) -> None:
        """
        Load additional alias entries from a JSON file.

        Expected format:
        [
            {"canonical_name": "Technology X", "category": "Category", "aliases": ["a", "b"]}
        ]
        """
        path = Path(alias_file)
        if not path.exists():
            logger.error(f"[TechnologyRegistry] Alias file not found: {alias_file}")
            raise FileNotFoundError(f"Alias file not found: {alias_file}")

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            logger.error(f"[TechnologyRegistry] Malformed alias file {alias_file}: {e}")
            raise

        if isinstance(data, dict):
            data = [data]

        loaded = 0
        for item in data:
            if not isinstance(item, dict):
                continue
            name = str(item.get("canonical_name", "")).strip()
            if not name:
                continue
            category = str(item.get("category", "Unknown")).strip()
            aliases = item.get("aliases", []) or []
            self.register(name, category, [str(a) for a in aliases])
            loaded += 1

        logger.info(f"[TechnologyRegistry] Loaded {loaded} entries from alias file '{alias_file}'.")
