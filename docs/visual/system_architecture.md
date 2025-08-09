# System Architecture Diagrams

## 🏗️ High-Level System Architecture

```mermaid

graph TB
    subgraph "Client Layer"
        UI[React Frontend Dashboard]
        API_CLIENT[API Clients]
        MOBILE[Mobile Apps]
    end

    subgraph "API Gateway"
        LB[Load Balancer]
        NGINX[Nginx Reverse Proxy]
        RATE[Rate Limiter]
    end

    subgraph "Application Layer"
        API[FastAPI Backend Server]
        WS[WebSocket Server]
        AUTH[Authentication Service]
        MIDDLEWARE[Security Middleware]
    end

    subgraph "Core Services"
        SCRAPER[Scraping Engine]
        CRAWLER[Crawling Engine]
        PROCESSOR[Data Processor]
        ANALYTICS[AI/ML Analytics]
        QUEUE[Queue Manager]
    end

    subgraph "Data Layer"
        SQLITE[(SQLite Database)]
        POSTGRES[(PostgreSQL)]
        REDIS[(Redis Cache)]
        FILES[File Storage]
    end

    subgraph "Monitoring & Logging"
        PROMETHEUS[Prometheus]
        GRAFANA[Grafana]
        LOGS[Structured Logging]
        HEALTH[Health Checks]
    end

    subgraph "External Systems"
        WEBSITES[Target Websites]
        APIS[External APIs]
        WEBHOOKS[Webhook Endpoints]
    end

    %% Connections
    UI --> LB
    API_CLIENT --> LB
    MOBILE --> LB

    LB --> NGINX
    NGINX --> RATE
    RATE --> API

    API --> AUTH
    API --> MIDDLEWARE
    API --> WS

    API --> SCRAPER
    API --> CRAWLER
    API --> PROCESSOR
    API --> ANALYTICS
    API --> QUEUE

    SCRAPER --> WEBSITES
    CRAWLER --> WEBSITES
    PROCESSOR --> APIS

    SCRAPER --> SQLITE
    CRAWLER --> POSTGRES
    PROCESSOR --> REDIS
    ANALYTICS --> FILES

    API --> PROMETHEUS
    SCRAPER --> LOGS
    PROCESSOR --> HEALTH

    PROMETHEUS --> GRAFANA

    %% Styling
    classDef clientLayer fill:#e1f5fe
    classDef apiGateway fill:#f3e5f5
    classDef appLayer fill:#e8f5e8
    classDef coreServices fill:#fff3e0
    classDef dataLayer fill:#fce4ec
    classDef monitoring fill:#f1f8e9
    classDef external fill:#f5f5f5

    class UI,API_CLIENT,MOBILE clientLayer
    class LB,NGINX,RATE apiGateway
    class API,WS,AUTH,MIDDLEWARE appLayer
    class SCRAPER,CRAWLER,PROCESSOR,ANALYTICS,QUEUE coreServices
    class SQLITE,POSTGRES,REDIS,FILES dataLayer
    class PROMETHEUS,GRAFANA,LOGS,HEALTH monitoring
    class WEBSITES,APIS,WEBHOOKS external

```

## 🔄 Data Flow Architecture

```mermaid

graph LR
    subgraph "Input Sources"
        USER[User Interface]
        API_REQ[API Requests]
        SCHEDULER[Scheduled Jobs]
    end

    subgraph "Request Processing"
        VALIDATION[Input Validation]
        AUTH_CHECK[Authentication]
        RATE_LIMIT[Rate Limiting]
        QUEUE_MGR[Queue Manager]
    end

    subgraph "Data Collection"
        CRAWLER[Web Crawler]
        SCRAPER[Data Scraper]
        EXTRACTOR[Content Extractor]
    end

    subgraph "Data Processing"
        CLEANER[Data Cleaner]
        NORMALIZER[Data Normalizer]
        ENRICHER[Data Enricher]
        VALIDATOR[Data Validator]
    end

    subgraph "AI/ML Pipeline"
        ANALYZER[Content Analyzer]
        CLASSIFIER[Content Classifier]
        PREDICTOR[Trend Predictor]
        INSIGHTS[Insight Generator]
    end

    subgraph "Storage Layer"
        CACHE[Redis Cache]
        DATABASE[SQLite/PostgreSQL]
        FILES[File Storage]
        ARCHIVE[Archive Storage]
    end

    subgraph "Output Layer"
        DASHBOARD[Real-time Dashboard]
        REPORTS[Generated Reports]
        ALERTS[Smart Alerts]
        EXPORTS[Data Exports]
    end

    %% Flow connections
    USER --> VALIDATION
    API_REQ --> VALIDATION
    SCHEDULER --> VALIDATION

    VALIDATION --> AUTH_CHECK
    AUTH_CHECK --> RATE_LIMIT
    RATE_LIMIT --> QUEUE_MGR

    QUEUE_MGR --> CRAWLER
    QUEUE_MGR --> SCRAPER

    CRAWLER --> EXTRACTOR
    SCRAPER --> EXTRACTOR
    EXTRACTOR --> CLEANER

    CLEANER --> NORMALIZER
    NORMALIZER --> ENRICHER
    ENRICHER --> VALIDATOR

    VALIDATOR --> CACHE
    VALIDATOR --> DATABASE
    VALIDATOR --> ANALYZER

    ANALYZER --> CLASSIFIER
    CLASSIFIER --> PREDICTOR
    PREDICTOR --> INSIGHTS

    DATABASE --> DASHBOARD
    INSIGHTS --> DASHBOARD
    CACHE --> DASHBOARD

    DATABASE --> REPORTS
    INSIGHTS --> ALERTS
    DATABASE --> EXPORTS

    %% Styling
    classDef input fill:#e3f2fd
    classDef processing fill:#f1f8e9
    classDef collection fill:#fff3e0
    classDef dataProc fill:#fce4ec
    classDef ai fill:#f3e5f5
    classDef storage fill:#e8f5e8
    classDef output fill:#e1f5fe

    class USER,API_REQ,SCHEDULER input
    class VALIDATION,AUTH_CHECK,RATE_LIMIT,QUEUE_MGR processing
    class CRAWLER,SCRAPER,EXTRACTOR collection
    class CLEANER,NORMALIZER,ENRICHER,VALIDATOR dataProc
    class ANALYZER,CLASSIFIER,PREDICTOR,INSIGHTS ai
    class CACHE,DATABASE,FILES,ARCHIVE storage
    class DASHBOARD,REPORTS,ALERTS,EXPORTS output

```

## 🔧 Component Interaction Diagram

```mermaid

graph TB
    subgraph "Frontend Components"
        REACT[React Dashboard]
        CHARTS[Chart Components]
        FORMS[Form Components]
        TABLES[Data Tables]
    end

    subgraph "Backend Services"
        FASTAPI[FastAPI Router]
        WEBSOCKET[WebSocket Handler]
        MIDDLEWARE[Security Middleware]
        BACKGROUND[Background Tasks]
    end

    subgraph "Core Engines"
        SCRAPING[Scraping Engine]
        CRAWLING[Crawling Engine]
        PROCESSING[Processing Engine]
        ANALYTICS[Analytics Engine]
    end

    subgraph "Data Management"
        CONNECTION[Connection Pool]
        QUERY[Query Builder]
        CACHE_MGR[Cache Manager]
        FILE_MGR[File Manager]
    end

    subgraph "Configuration"
        ENV_CONFIG[Environment Config]
        DB_CONFIG[Database Config]
        SECURITY_CONFIG[Security Config]
        LOGGING_CONFIG[Logging Config]
    end

    %% Interactions
    REACT --> FASTAPI
    CHARTS --> WEBSOCKET
    FORMS --> MIDDLEWARE
    TABLES --> BACKGROUND

    FASTAPI --> SCRAPING
    WEBSOCKET --> CRAWLING
    MIDDLEWARE --> PROCESSING
    BACKGROUND --> ANALYTICS

    SCRAPING --> CONNECTION
    CRAWLING --> QUERY
    PROCESSING --> CACHE_MGR
    ANALYTICS --> FILE_MGR

    CONNECTION --> ENV_CONFIG
    QUERY --> DB_CONFIG
    CACHE_MGR --> SECURITY_CONFIG
    FILE_MGR --> LOGGING_CONFIG

    %% Styling
    classDef frontend fill:#e3f2fd
    classDef backend fill:#f1f8e9
    classDef engines fill:#fff3e0
    classDef dataManagement fill:#fce4ec
    classDef config fill:#f3e5f5

    class REACT,CHARTS,FORMS,TABLES frontend
    class FASTAPI,WEBSOCKET,MIDDLEWARE,BACKGROUND backend
    class SCRAPING,CRAWLING,PROCESSING,ANALYTICS engines
    class CONNECTION,QUERY,CACHE_MGR,FILE_MGR dataManagement
    class ENV_CONFIG,DB_CONFIG,SECURITY_CONFIG,LOGGING_CONFIG config

```

## 🚀 Deployment Architecture

```mermaid

graph TB
    subgraph "Production Environment"
        subgraph "Container Orchestration"
            DOCKER[Docker Containers]
            COMPOSE[Docker Compose]
            SWARM[Docker Swarm/K8s]
        end

        subgraph "Load Balancing"
            LB[Load Balancer]
            HEALTH_CHECK[Health Checks]
            FAILOVER[Failover System]
        end

        subgraph "Application Instances"
            APP1[App Instance 1]
            APP2[App Instance 2]
            APP3[App Instance 3]
        end

        subgraph "Database Cluster"
            DB_PRIMARY[(Primary DB)]
            DB_REPLICA[(Replica DB)]
            DB_CACHE[(Redis Cluster)]
        end

        subgraph "Monitoring Stack"
            PROMETHEUS[Prometheus]
            GRAFANA[Grafana]
            ALERTMANAGER[AlertManager]
        end

        subgraph "Security Layer"
            SSL[SSL/TLS Termination]
            WAF[Web Application Firewall]
            SECRETS[Secret Management]
        end
    end

    subgraph "External Services"
        CDN[Content Delivery Network]
        BACKUP[Backup Storage]
        LOGS[Log Aggregation]
    end

    %% Connections
    CDN --> LB
    LB --> SSL
    SSL --> WAF
    WAF --> HEALTH_CHECK
    HEALTH_CHECK --> FAILOVER

    FAILOVER --> APP1
    FAILOVER --> APP2
    FAILOVER --> APP3

    APP1 --> DB_PRIMARY
    APP2 --> DB_REPLICA
    APP3 --> DB_CACHE

    APP1 --> PROMETHEUS
    APP2 --> PROMETHEUS
    APP3 --> PROMETHEUS

    PROMETHEUS --> GRAFANA
    PROMETHEUS --> ALERTMANAGER

    COMPOSE --> DOCKER
    DOCKER --> SWARM

    APP1 --> BACKUP
    APP2 --> LOGS
    SECRETS --> APP3

    %% Styling
    classDef orchestration fill:#e3f2fd
    classDef loadBalancing fill:#f1f8e9
    classDef application fill:#fff3e0
    classDef database fill:#fce4ec
    classDef monitoring fill:#f3e5f5
    classDef security fill:#e8f5e8
    classDef external fill:#f5f5f5

    class DOCKER,COMPOSE,SWARM orchestration
    class LB,HEALTH_CHECK,FAILOVER loadBalancing
    class APP1,APP2,APP3 application
    class DB_PRIMARY,DB_REPLICA,DB_CACHE database
    class PROMETHEUS,GRAFANA,ALERTMANAGER monitoring
    class SSL,WAF,SECRETS security
    class CDN,BACKUP,LOGS external

```

## 📱 User Interface Architecture

```mermaid

graph TB
    subgraph "Frontend Layer"
        subgraph "React Components"
            LAYOUT[Layout Component]
            NAVIGATION[Navigation Component]
            SIDEBAR[Sidebar Component]
            HEADER[Header Component]
        end

        subgraph "Feature Components"
            DASHBOARD[Dashboard View]
            SCRAPING[Scraping Interface]
            ANALYTICS[Analytics Dashboard]
            SETTINGS[Settings Panel]
        end

        subgraph "UI Components"
            CHARTS[Chart Library]
            TABLES[Data Tables]
            FORMS[Form Components]
            MODALS[Modal Dialogs]
        end

        subgraph "State Management"
            REDUX[Redux Store]
            CONTEXT[React Context]
            HOOKS[Custom Hooks]
            MIDDLEWARE[Redux Middleware]
        end
    end

    subgraph "API Layer"
        REST[REST API Client]
        WEBSOCKET[WebSocket Client]
        CACHE[Client Cache]
        INTERCEPTORS[Request Interceptors]
    end

    subgraph "Backend Services"
        ENDPOINTS[API Endpoints]
        REALTIME[Real-time Updates]
        AUTH[Authentication]
        VALIDATION[Request Validation]
    end

    %% Connections
    LAYOUT --> NAVIGATION
    LAYOUT --> SIDEBAR
    LAYOUT --> HEADER

    NAVIGATION --> DASHBOARD
    NAVIGATION --> SCRAPING
    NAVIGATION --> ANALYTICS
    NAVIGATION --> SETTINGS

    DASHBOARD --> CHARTS
    SCRAPING --> TABLES
    ANALYTICS --> FORMS
    SETTINGS --> MODALS

    CHARTS --> REDUX
    TABLES --> CONTEXT
    FORMS --> HOOKS
    MODALS --> MIDDLEWARE

    REDUX --> REST
    CONTEXT --> WEBSOCKET
    HOOKS --> CACHE
    MIDDLEWARE --> INTERCEPTORS

    REST --> ENDPOINTS
    WEBSOCKET --> REALTIME
    CACHE --> AUTH
    INTERCEPTORS --> VALIDATION

    %% Styling
    classDef react fill:#e3f2fd
    classDef features fill:#f1f8e9
    classDef ui fill:#fff3e0
    classDef state fill:#fce4ec
    classDef api fill:#f3e5f5
    classDef backend fill:#e8f5e8

    class LAYOUT,NAVIGATION,SIDEBAR,HEADER react
    class DASHBOARD,SCRAPING,ANALYTICS,SETTINGS features
    class CHARTS,TABLES,FORMS,MODALS ui
    class REDUX,CONTEXT,HOOKS,MIDDLEWARE state
    class REST,WEBSOCKET,CACHE,INTERCEPTORS api
    class ENDPOINTS,REALTIME,AUTH,VALIDATION backend

```

## 🔐 Security Architecture

```mermaid

graph TB
    subgraph "Security Perimeter"
        subgraph "Network Security"
            FIREWALL[Firewall Rules]
            DDoS[DDoS Protection]
            VPN[VPN Access]
        end

        subgraph "Application Security"
            WAF[Web Application Firewall]
            RATE_LIMIT[Rate Limiting]
            INPUT_VAL[Input Validation]
            OUTPUT_ENC[Output Encoding]
        end

        subgraph "Authentication & Authorization"
            JWT[JWT Tokens]
            RBAC[Role-Based Access]
            MFA[Multi-Factor Auth]
            SESSION[Session Management]
        end

        subgraph "Data Security"
            ENCRYPTION[Data Encryption]
            HASHING[Password Hashing]
            SANITIZATION[Data Sanitization]
            MASKING[Data Masking]
        end

        subgraph "Monitoring & Auditing"
            LOGGING[Security Logging]
            SIEM[SIEM Integration]
            ALERTS[Security Alerts]
            FORENSICS[Digital Forensics]
        end
    end

    subgraph "Compliance & Governance"
        POLICIES[Security Policies]
        COMPLIANCE[Compliance Checks]
        AUDIT[Security Audits]
        TRAINING[Security Training]
    end

    %% Security Flow
    FIREWALL --> WAF
    DDoS --> RATE_LIMIT
    VPN --> INPUT_VAL

    WAF --> JWT
    RATE_LIMIT --> RBAC
    INPUT_VAL --> MFA
    OUTPUT_ENC --> SESSION

    JWT --> ENCRYPTION
    RBAC --> HASHING
    MFA --> SANITIZATION
    SESSION --> MASKING

    ENCRYPTION --> LOGGING
    HASHING --> SIEM
    SANITIZATION --> ALERTS
    MASKING --> FORENSICS

    LOGGING --> POLICIES
    SIEM --> COMPLIANCE
    ALERTS --> AUDIT
    FORENSICS --> TRAINING

    %% Styling
    classDef network fill:#ffebee
    classDef application fill:#f3e5f5
    classDef auth fill:#e8f5e8
    classDef data fill:#e3f2fd
    classDef monitoring fill:#fff3e0
    classDef governance fill:#f1f8e9

    class FIREWALL,DDoS,VPN network
    class WAF,RATE_LIMIT,INPUT_VAL,OUTPUT_ENC application
    class JWT,RBAC,MFA,SESSION auth
    class ENCRYPTION,HASHING,SANITIZATION,MASKING data
    class LOGGING,SIEM,ALERTS,FORENSICS monitoring
    class POLICIES,COMPLIANCE,AUDIT,TRAINING governance

```
