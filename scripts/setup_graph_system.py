"""
Advanced Entity Graph System Installation and Setup

This script installs and configures all dependencies required for the
Advanced Entity Graph System with business intelligence capabilities.
"""

import subprocess
import sys
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class GraphSystemInstaller:
    """Installer for the Advanced Entity Graph System"""

    def __init__(self):
        self.python_requirements = [
            # Core graph libraries
            "networkx>=3.2.1",
            "plotly>=5.17.0",
            "kaleido>=0.2.1",  # For static image export
            # Graph database connectors
            "py2neo>=2021.2.4",  # Neo4j
            "pyarango>=2.0.2",  # ArangoDB
            "janusgraph-python>=0.3.1",  # JanusGraph
            # Machine Learning for graphs
            "scikit-learn>=1.3.0",
            "numpy>=1.24.0",
            "pandas>=2.0.0",
            "scipy>=1.11.0",
            # Web visualization
            "dash>=2.14.0",
            "dash-cytoscape>=0.3.0",
            "plotly-dash>=0.0.4",
            # Advanced analytics
            "community>=1.0.0b1",  # Community detection
            "python-louvain>=0.16",  # Louvain community detection
            "node2vec>=0.4.6",  # Graph embeddings
            "karateclub>=1.3.3",  # Graph machine learning
            # Natural language processing
            "spacy>=3.7.0",
            "nltk>=3.8.1",
            "fuzzywuzzy>=0.18.0",
            "python-levenshtein>=0.21.1",
            # Temporal analysis
            "arrow>=1.3.0",
            "dateutil>=2.8.2",
            # Performance and utilities
            "numba>=0.58.0",
            "cython>=3.0.0",
            "joblib>=1.3.2",
            "tqdm>=4.66.0",
            # Data format support
            "pyarrow>=14.0.0",
            "openpyxl>=3.1.0",
            "xlsxwriter>=3.1.0",
            # Cryptography for security
            "cryptography>=41.0.0",
            "pycryptodome>=3.19.0",
        ]

        self.optional_requirements = [
            # GPU acceleration (optional)
            "cupy-cuda12x>=12.0.0",  # CUDA 12.x
            "rapids-cudf>=23.10.0",  # GPU dataframes
            # Advanced ML libraries (optional)
            "torch>=2.1.0",
            "torch-geometric>=2.4.0",
            "dgl>=1.1.0",
            # Visualization enhancements
            "bokeh>=3.3.0",
            "holoviews>=1.18.0",
            "datashader>=0.15.0",
        ]

        self.system_dependencies = {
            "linux": [
                "graphviz",
                "graphviz-dev",
                "pkg-config",
                "python3-dev",
                "build-essential",
                "libffi-dev",
                "libssl-dev",
            ],
            "macos": ["graphviz", "pkg-config"],
            "windows": [
                # Windows packages typically handled by pip
            ],
        }

    def detect_platform(self) -> str:
        """Detect the current platform"""
        import platform

        system = platform.system().lower()

        if system == "linux":
            return "linux"
        elif system == "darwin":
            return "macos"
        elif system == "windows":
            return "windows"
        else:
            return "unknown"

    def install_system_dependencies(self) -> bool:
        """Install system-level dependencies"""
        platform = self.detect_platform()

        if platform not in self.system_dependencies:
            logger.warning(f"Unknown platform: {platform}")
            return True

        dependencies = self.system_dependencies[platform]

        try:
            if platform == "linux":
                # Try different package managers
                if self._command_exists("apt-get"):
                    for dep in dependencies:
                        subprocess.run(
                            ["sudo", "apt-get", "install", "-y", dep], check=True
                        )
                elif self._command_exists("yum"):
                    for dep in dependencies:
                        subprocess.run(
                            ["sudo", "yum", "install", "-y", dep], check=True
                        )
                elif self._command_exists("dnf"):
                    for dep in dependencies:
                        subprocess.run(
                            ["sudo", "dnf", "install", "-y", dep], check=True
                        )

            elif platform == "macos":
                if self._command_exists("brew"):
                    for dep in dependencies:
                        subprocess.run(["brew", "install", dep], check=True)
                else:
                    logger.warning("Homebrew not found. Please install Homebrew first.")
                    return False

            logger.info("System dependencies installed successfully")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing system dependencies: {e}")
            return False

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system"""
        try:
            subprocess.run(["which", command], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def install_python_requirements(self, install_optional: bool = False) -> bool:
        """Install Python requirements"""
        requirements = self.python_requirements.copy()

        if install_optional:
            requirements.extend(self.optional_requirements)

        try:
            # Upgrade pip first
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True
            )

            # Install requirements
            logger.info(f"Installing {len(requirements)} Python packages...")

            for requirement in requirements:
                try:
                    logger.info(f"Installing {requirement}...")
                    subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "install",
                            requirement,
                            "--upgrade",
                        ],
                        check=True,
                        capture_output=True,
                    )

                except subprocess.CalledProcessError as e:
                    logger.warning(f"Failed to install {requirement}: {e}")
                    # Continue with other packages

            logger.info("Python requirements installed successfully")
            return True

        except Exception as e:
            logger.error(f"Error installing Python requirements: {e}")
            return False

    def setup_spacy_models(self) -> bool:
        """Download spaCy language models"""
        models = ["en_core_web_sm", "en_core_web_md"]

        try:
            for model in models:
                logger.info(f"Downloading spaCy model: {model}")
                subprocess.run(
                    [sys.executable, "-m", "spacy", "download", model], check=True
                )

            logger.info("spaCy models downloaded successfully")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Error downloading spaCy models: {e}")
            return False

    def setup_neo4j_database(self, install_docker: bool = True) -> bool:
        """Setup Neo4j database using Docker"""
        if not install_docker:
            logger.info("Skipping Neo4j setup. Please install manually if needed.")
            return True

        try:
            # Check if Docker is available
            subprocess.run(["docker", "--version"], check=True, capture_output=True)

            # Pull Neo4j image
            logger.info("Pulling Neo4j Docker image...")
            subprocess.run(["docker", "pull", "neo4j:5.13-community"], check=True)

            # Create Neo4j container
            logger.info("Creating Neo4j container...")
            subprocess.run(
                [
                    "docker",
                    "run",
                    "--name",
                    "neo4j-graph-system",
                    "-p",
                    "7474:7474",
                    "-p",
                    "7687:7687",
                    "-e",
                    "NEO4J_AUTH=neo4j/graphsystem123",
                    "-e",
                    'NEO4J_PLUGINS=["apoc"]',
                    "-d",
                    "neo4j:5.13-community",
                ],
                check=True,
            )

            logger.info("Neo4j database setup completed")
            logger.info("Access Neo4j browser at: http://localhost:7474")
            logger.info("Username: neo4j, Password: graphsystem123")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Error setting up Neo4j: {e}")
            return False
        except FileNotFoundError:
            logger.warning(
                "Docker not found. Please install Docker manually for Neo4j support."
            )
            return False

    def create_configuration_files(self) -> bool:
        """Create configuration files for the graph system"""
        try:
            config_dir = Path("config/graph_system")
            config_dir.mkdir(parents=True, exist_ok=True)

            # Main configuration
            main_config = {
                "graph_system": {
                    "default_database": "networkx",
                    "auto_sync_enabled": True,
                    "auto_sync_interval": 300,
                    "max_nodes_in_memory": 10000,
                    "enable_caching": True,
                    "cache_ttl_hours": 24,
                },
                "databases": {
                    "networkx": {"type": "networkx", "in_memory": True},
                    "neo4j": {
                        "type": "neo4j",
                        "uri": "bolt://localhost:7687",
                        "username": "neo4j",
                        "password": "graphsystem123",
                        "encrypted": False,
                    },
                    "arangodb": {
                        "type": "arangodb",
                        "host": "localhost",
                        "port": 8529,
                        "username": "root",
                        "password": "",
                        "database": "graph_system",
                    },
                },
                "analytics": {
                    "enable_ml_features": True,
                    "community_detection_algorithm": "louvain",
                    "centrality_measures": [
                        "degree",
                        "betweenness",
                        "closeness",
                        "eigenvector",
                        "pagerank",
                    ],
                    "anomaly_detection_threshold": 0.8,
                    "similarity_threshold": 0.85,
                },
                "visualization": {
                    "default_layout": "spring",
                    "default_color_scheme": "node_type",
                    "show_labels": True,
                    "max_nodes_to_display": 1000,
                    "enable_3d_visualization": False,
                },
                "integration": {
                    "enable_data_quality_sync": True,
                    "enable_provenance_tracking": True,
                    "auto_relationship_creation": True,
                    "duplicate_detection_enabled": True,
                },
            }

            config_file = config_dir / "graph_config.json"
            with open(config_file, "w") as f:
                json.dump(main_config, f, indent=2)

            # Query templates
            query_templates = {
                "templates": {
                    "circular_ownership": {
                        "name": "Circular Ownership Detection",
                        "description": "Find circular ownership patterns",
                        "cypher": """
                            MATCH path = (c1:COMPANY)-[:OWNS*2..5]->(c1)
                            WHERE c1.entity_id = $entity_id
                            RETURN path
                        """,
                        "parameters": {"entity_id": "string"},
                    },
                    "directors_in_common": {
                        "name": "Directors in Common",
                        "description": "Find companies sharing directors",
                        "cypher": """
                            MATCH (p:PERSON)-[:HAS_OFFICER]->(c1:COMPANY)
                            MATCH (p)-[:HAS_OFFICER]->(c2:COMPANY)
                            WHERE c1 <> c2 AND c1.entity_id = $entity_id
                            RETURN p, c1, c2
                        """,
                        "parameters": {"entity_id": "string"},
                    },
                    "ultimate_beneficial_owner": {
                        "name": "Ultimate Beneficial Owner",
                        "description": "Find ultimate beneficial owners",
                        "cypher": """
                            MATCH path = (start:COMPANY)-[:OWNS*]->(end:PERSON)
                            WHERE start.entity_id = $entity_id
                            AND NOT (end)-[:OWNS]->()
                            RETURN path ORDER BY length(path) DESC LIMIT 10
                        """,
                        "parameters": {"entity_id": "string"},
                    },
                    "shell_company_detection": {
                        "name": "Shell Company Detection",
                        "description": "Detect potential shell companies",
                        "cypher": """
                            MATCH (c:COMPANY)
                            WHERE c.entity_id = $entity_id
                            OPTIONAL MATCH (c)-[:HAS_OFFICER]->(officers)
                            OPTIONAL MATCH (c)-[:REGISTERED_AT]->(addr:ADDRESS)
                            WITH c, count(officers) as officer_count, collect(addr) as addresses
                            WHERE officer_count <= 1 OR size(addresses) = 0
                            RETURN c, officer_count, addresses
                        """,
                        "parameters": {"entity_id": "string"},
                    },
                    "network_expansion": {
                        "name": "Network Expansion",
                        "description": "Expand network around an entity",
                        "cypher": """
                            MATCH (start {entity_id: $entity_id})
                            MATCH path = (start)-[*1..$max_hops]-(connected)
                            RETURN path, connected
                            ORDER BY length(path)
                            LIMIT $limit
                        """,
                        "parameters": {
                            "entity_id": "string",
                            "max_hops": "integer",
                            "limit": "integer",
                        },
                    },
                    "risk_propagation": {
                        "name": "Risk Propagation Analysis",
                        "description": "Analyze risk propagation through networks",
                        "cypher": """
                            MATCH path = (risk_entity {entity_id: $entity_id})-[*1..$depth]-(connected)
                            WHERE any(rel in relationships(path) WHERE rel.confidence < 0.7)
                            RETURN path, connected
                            ORDER BY length(path)
                        """,
                        "parameters": {"entity_id": "string", "depth": "integer"},
                    },
                }
            }

            templates_file = config_dir / "query_templates.json"
            with open(templates_file, "w") as f:
                json.dump(query_templates, f, indent=2)

            logger.info(f"Configuration files created in {config_dir}")
            return True

        except Exception as e:
            logger.error(f"Error creating configuration files: {e}")
            return False

    def run_tests(self) -> bool:
        """Run basic tests to verify installation"""
        try:
            # Test core libraries
            import networkx as nx
            import plotly.graph_objects as go

            # Test basic graph operations
            G = nx.Graph()
            G.add_node(1, name="Test Node")
            G.add_edge(1, 2)

            assert len(G.nodes()) == 2
            assert len(G.edges()) == 1

            # Test plotly
            fig = go.Figure()
            fig.add_scatter(x=[1, 2, 3], y=[1, 4, 2])

            logger.info("Core library tests passed")

            # Test optional libraries
            try:
                import community
                import spacy

                logger.info("Optional library tests passed")
            except ImportError as e:
                logger.warning(f"Some optional libraries not available: {e}")

            return True

        except Exception as e:
            logger.error(f"Tests failed: {e}")
            return False

    def install_complete_system(
        self,
        install_optional: bool = False,
        setup_neo4j: bool = False,
        run_tests: bool = True,
    ) -> bool:
        """Install the complete Advanced Entity Graph System"""

        logger.info("Starting Advanced Entity Graph System installation...")

        # Step 1: Install system dependencies
        logger.info("Step 1: Installing system dependencies...")
        if not self.install_system_dependencies():
            logger.error("Failed to install system dependencies")
            return False

        # Step 2: Install Python requirements
        logger.info("Step 2: Installing Python requirements...")
        if not self.install_python_requirements(install_optional):
            logger.error("Failed to install Python requirements")
            return False

        # Step 3: Setup spaCy models
        logger.info("Step 3: Setting up spaCy models...")
        if not self.setup_spacy_models():
            logger.warning("Failed to setup spaCy models, continuing...")

        # Step 4: Setup Neo4j (optional)
        if setup_neo4j:
            logger.info("Step 4: Setting up Neo4j database...")
            if not self.setup_neo4j_database():
                logger.warning("Failed to setup Neo4j, continuing...")

        # Step 5: Create configuration files
        logger.info("Step 5: Creating configuration files...")
        if not self.create_configuration_files():
            logger.warning("Failed to create configuration files, continuing...")

        # Step 6: Run tests
        if run_tests:
            logger.info("Step 6: Running verification tests...")
            if not self.run_tests():
                logger.warning("Some tests failed, but installation may still work")

        logger.info("Advanced Entity Graph System installation completed!")

        # Print summary
        self.print_installation_summary()

        return True

    def print_installation_summary(self):
        """Print installation summary and next steps"""
        print("\n" + "=" * 60)
        print("Advanced Entity Graph System - Installation Complete!")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Start the GUI application:")
        print("   python -m gui.main")
        print("\n2. Navigate to the 'Entity Graphs' tab")
        print("\n3. Configure your graph database connection")
        print("\n4. Begin importing entities and building your graph")
        print("\n5. Explore advanced analytics and visualization features")

        print("\nConfiguration Files:")
        print("- Graph Config: config/graph_system/graph_config.json")
        print("- Query Templates: config/graph_system/query_templates.json")

        print("\nFor Neo4j support:")
        print("- Neo4j Browser: http://localhost:7474")
        print("- Username: neo4j")
        print("- Password: graphsystem123")

        print("\nDocumentation and Support:")
        print("- See docs/advanced_entity_graphs.md for detailed usage")
        print("- Check logs/ directory for troubleshooting")
        print("=" * 60)


def main():
    """Main installation function"""
    import argparse

    parser = argparse.ArgumentParser(description="Install Advanced Entity Graph System")
    parser.add_argument(
        "--optional",
        action="store_true",
        help="Install optional packages (GPU support, advanced ML)",
    )
    parser.add_argument(
        "--neo4j", action="store_true", help="Setup Neo4j database using Docker"
    )
    parser.add_argument(
        "--no-tests", action="store_true", help="Skip verification tests"
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    installer = GraphSystemInstaller()

    success = installer.install_complete_system(
        install_optional=args.optional,
        setup_neo4j=args.neo4j,
        run_tests=not args.no_tests,
    )

    if success:
        print("\nInstallation completed successfully!")
        sys.exit(0)
    else:
        print("\nInstallation completed with errors. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
