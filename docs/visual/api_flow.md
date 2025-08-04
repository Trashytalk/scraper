# API Flow Diagrams

## 🌐 REST API Flow Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB_CLIENT[Web Client]
        MOBILE_APP[Mobile App]
        CLI_TOOL[CLI Tool]
        EXTERNAL_API[External API Client]
    end
    
    subgraph "API Gateway"
        LOAD_BALANCER[Load Balancer]
        RATE_LIMITER[Rate Limiter]
        API_ROUTER[API Router]
        MIDDLEWARE[Middleware Stack]
    end
    
    subgraph "Authentication Layer"
        JWT_AUTH[JWT Authentication]
        SESSION_MANAGER[Session Manager]
        USER_RESOLVER[User Resolver]
        PERMISSION_CHECK[Permission Check]
    end
    
    subgraph "Request Processing"
        INPUT_VALIDATION[Input Validation]
        REQUEST_PARSER[Request Parser]
        BUSINESS_LOGIC[Business Logic]
        DATA_ACCESS[Data Access Layer]
    end
    
    subgraph "Response Processing"
        DATA_SERIALIZATION[Data Serialization]
        RESPONSE_FORMATTER[Response Formatter]
        COMPRESSION[Response Compression]
        CACHING[Response Caching]
    end
    
    subgraph "Error Handling"
        EXCEPTION_HANDLER[Exception Handler]
        ERROR_FORMATTER[Error Formatter]
        LOGGING[Error Logging]
        MONITORING[Error Monitoring]
    end
    
    %% Request flow
    WEB_CLIENT --> LOAD_BALANCER
    MOBILE_APP --> LOAD_BALANCER
    CLI_TOOL --> LOAD_BALANCER
    EXTERNAL_API --> LOAD_BALANCER
    
    LOAD_BALANCER --> RATE_LIMITER
    RATE_LIMITER --> API_ROUTER
    API_ROUTER --> MIDDLEWARE
    
    MIDDLEWARE --> JWT_AUTH
    JWT_AUTH --> SESSION_MANAGER
    SESSION_MANAGER --> USER_RESOLVER
    USER_RESOLVER --> PERMISSION_CHECK
    
    PERMISSION_CHECK --> INPUT_VALIDATION
    INPUT_VALIDATION --> REQUEST_PARSER
    REQUEST_PARSER --> BUSINESS_LOGIC
    BUSINESS_LOGIC --> DATA_ACCESS
    
    DATA_ACCESS --> DATA_SERIALIZATION
    DATA_SERIALIZATION --> RESPONSE_FORMATTER
    RESPONSE_FORMATTER --> COMPRESSION
    COMPRESSION --> CACHING
    
    %% Error flow
    INPUT_VALIDATION --> EXCEPTION_HANDLER
    BUSINESS_LOGIC --> EXCEPTION_HANDLER
    DATA_ACCESS --> EXCEPTION_HANDLER
    
    EXCEPTION_HANDLER --> ERROR_FORMATTER
    ERROR_FORMATTER --> LOGGING
    LOGGING --> MONITORING
    
    %% Styling
    classDef client fill:#e3f2fd
    classDef gateway fill:#f1f8e9
    classDef auth fill:#e8f5e8
    classDef processing fill:#fff3e0
    classDef response fill:#f3e5f5
    classDef error fill:#ffebee
    
    class WEB_CLIENT,MOBILE_APP,CLI_TOOL,EXTERNAL_API client
    class LOAD_BALANCER,RATE_LIMITER,API_ROUTER,MIDDLEWARE gateway
    class JWT_AUTH,SESSION_MANAGER,USER_RESOLVER,PERMISSION_CHECK auth
    class INPUT_VALIDATION,REQUEST_PARSER,BUSINESS_LOGIC,DATA_ACCESS processing
    class DATA_SERIALIZATION,RESPONSE_FORMATTER,COMPRESSION,CACHING response
    class EXCEPTION_HANDLER,ERROR_FORMATTER,LOGGING,MONITORING error
```

## 🔄 WebSocket Real-time Flow

```mermaid
sequenceDiagram
    participant Client
    participant Gateway
    participant Auth
    participant WebSocket
    participant EventBus
    participant Database
    participant Analytics
    
    Note over Client,Analytics: WebSocket Connection Setup
    Client->>Gateway: WS Connection Request
    Gateway->>Auth: Validate JWT Token
    Auth->>Gateway: Token Valid
    Gateway->>WebSocket: Establish Connection
    WebSocket->>Client: Connection Confirmed
    
    Note over Client,Analytics: Real-time Data Subscription
    Client->>WebSocket: Subscribe to scraping updates
    WebSocket->>EventBus: Register subscription
    EventBus->>WebSocket: Subscription confirmed
    
    Note over Client,Analytics: Data Processing Events
    Database->>EventBus: New scraping data
    EventBus->>Analytics: Process analytics
    Analytics->>EventBus: Analytics complete
    EventBus->>WebSocket: Notify subscribers
    WebSocket->>Client: Real-time update
    
    Note over Client,Analytics: Bi-directional Communication
    Client->>WebSocket: Send command
    WebSocket->>EventBus: Broadcast command
    EventBus->>Database: Execute command
    Database->>EventBus: Command result
    EventBus->>WebSocket: Result notification
    WebSocket->>Client: Command response
    
    Note over Client,Analytics: Error Handling
    Database->>EventBus: Error occurred
    EventBus->>WebSocket: Error notification
    WebSocket->>Client: Error message
    Client->>WebSocket: Acknowledge error
    
    Note over Client,Analytics: Connection Cleanup
    Client->>WebSocket: Disconnect request
    WebSocket->>EventBus: Unsubscribe all
    EventBus->>WebSocket: Cleanup complete
    WebSocket->>Client: Connection closed
```

## 📊 Analytics API Flow

```mermaid
graph LR
    subgraph "Data Request"
        CLIENT[Analytics Client]
        QUERY[Query Builder]
        FILTERS[Data Filters]
        AGGREGATION[Aggregation Rules]
    end
    
    subgraph "Query Processing"
        VALIDATOR[Query Validator]
        OPTIMIZER[Query Optimizer]
        EXECUTION[Query Execution]
        CACHING[Result Caching]
    end
    
    subgraph "Data Sources"
        LIVE_DATA[(Live Data)]
        HISTORICAL[(Historical Data)]
        AGGREGATED[(Aggregated Data)]
        EXTERNAL[(External Sources)]
    end
    
    subgraph "Analytics Engine"
        PROCESSOR[Data Processor]
        ML_ENGINE[ML Engine]
        STATISTICS[Statistical Analysis]
        VISUALIZATION[Visualization Prep]
    end
    
    subgraph "Response Formatting"
        SERIALIZER[Data Serializer]
        FORMATTER[Response Formatter]
        COMPRESSOR[Data Compressor]
        DELIVERY[Response Delivery]
    end
    
    subgraph "Real-time Updates"
        STREAM[Data Stream]
        WEBSOCKET[WebSocket Notifier]
        PUSH[Push Notifications]
        ALERTS[Alert System]
    end
    
    %% Flow connections
    CLIENT --> QUERY
    QUERY --> FILTERS
    FILTERS --> AGGREGATION
    
    AGGREGATION --> VALIDATOR
    VALIDATOR --> OPTIMIZER
    OPTIMIZER --> EXECUTION
    EXECUTION --> CACHING
    
    EXECUTION --> LIVE_DATA
    EXECUTION --> HISTORICAL
    EXECUTION --> AGGREGATED
    EXECUTION --> EXTERNAL
    
    LIVE_DATA --> PROCESSOR
    HISTORICAL --> ML_ENGINE
    AGGREGATED --> STATISTICS
    EXTERNAL --> VISUALIZATION
    
    PROCESSOR --> SERIALIZER
    ML_ENGINE --> FORMATTER
    STATISTICS --> COMPRESSOR
    VISUALIZATION --> DELIVERY
    
    PROCESSOR --> STREAM
    ML_ENGINE --> WEBSOCKET
    STATISTICS --> PUSH
    VISUALIZATION --> ALERTS
    
    %% Styling
    classDef request fill:#e3f2fd
    classDef processing fill:#f1f8e9
    classDef sources fill:#e8f5e8
    classDef analytics fill:#fff3e0
    classDef formatting fill:#f3e5f5
    classDef realtime fill:#fce4ec
    
    class CLIENT,QUERY,FILTERS,AGGREGATION request
    class VALIDATOR,OPTIMIZER,EXECUTION,CACHING processing
    class LIVE_DATA,HISTORICAL,AGGREGATED,EXTERNAL sources
    class PROCESSOR,ML_ENGINE,STATISTICS,VISUALIZATION analytics
    class SERIALIZER,FORMATTER,COMPRESSOR,DELIVERY formatting
    class STREAM,WEBSOCKET,PUSH,ALERTS realtime
```

## 🕷️ Scraping API Workflow

```mermaid
stateDiagram-v2
    [*] --> RequestReceived
    
    state "Scraping Request Processing" {
        RequestReceived --> ValidationCheck
        ValidationCheck --> AuthenticationCheck
        AuthenticationCheck --> RateLimitCheck
        RateLimitCheck --> JobCreation
    }
    
    state "Job Management" {
        JobCreation --> JobQueued
        JobQueued --> JobScheduled
        JobScheduled --> JobExecuting
        JobExecuting --> JobMonitoring
    }
    
    state "Scraping Execution" {
        JobMonitoring --> CrawlerInitialized
        CrawlerInitialized --> URLDiscovery
        URLDiscovery --> ContentExtraction
        ContentExtraction --> DataProcessing
    }
    
    state "Data Processing" {
        DataProcessing --> DataValidation
        DataValidation --> DataCleaning
        DataCleaning --> DataEnrichment
        DataEnrichment --> DataStorage
    }
    
    state "Job Completion" {
        DataStorage --> ResultsGeneration
        ResultsGeneration --> NotificationSent
        NotificationSent --> JobCompleted
        JobCompleted --> [*]
    }
    
    state "Error Handling" {
        ValidationCheck --> ValidationError
        AuthenticationCheck --> AuthError
        RateLimitCheck --> RateLimitError
        JobExecuting --> ExecutionError
        DataProcessing --> ProcessingError
        
        ValidationError --> ErrorResponse
        AuthError --> ErrorResponse
        RateLimitError --> ErrorResponse
        ExecutionError --> JobFailed
        ProcessingError --> JobFailed
        
        JobFailed --> ErrorNotification
        ErrorNotification --> [*]
        ErrorResponse --> [*]
    }
    
    state "Progress Updates" {
        JobMonitoring --> ProgressUpdate
        URLDiscovery --> ProgressUpdate
        ContentExtraction --> ProgressUpdate
        DataProcessing --> ProgressUpdate
        
        ProgressUpdate --> WebSocketNotification
        WebSocketNotification --> ClientUpdate
    }
```

## 🔐 Authentication API Flow

```mermaid
graph TD
    subgraph "Authentication Request"
        LOGIN_REQUEST[Login Request]
        CREDENTIALS[User Credentials]
        MFA_TOKEN[MFA Token]
    end
    
    subgraph "Credential Validation"
        USERNAME_CHECK[Username Validation]
        PASSWORD_VERIFY[Password Verification]
        MFA_VERIFY[MFA Verification]
        ACCOUNT_STATUS[Account Status Check]
    end
    
    subgraph "Token Generation"
        JWT_CREATION[JWT Token Creation]
        REFRESH_TOKEN[Refresh Token]
        TOKEN_SIGNING[Token Signing]
        SESSION_CREATION[Session Creation]
    end
    
    subgraph "Security Measures"
        RATE_LIMITING[Rate Limiting]
        BRUTE_FORCE[Brute Force Protection]
        AUDIT_LOG[Audit Logging]
        SECURITY_ALERT[Security Alerts]
    end
    
    subgraph "Response Processing"
        TOKEN_RESPONSE[Token Response]
        USER_PROFILE[User Profile]
        PERMISSIONS[User Permissions]
        RESPONSE_HEADERS[Security Headers]
    end
    
    subgraph "Session Management"
        SESSION_STORAGE[Session Storage]
        SESSION_TRACKING[Session Tracking]
        SESSION_TIMEOUT[Session Timeout]
        LOGOUT_HANDLER[Logout Handler]
    end
    
    %% Authentication flow
    LOGIN_REQUEST --> USERNAME_CHECK
    CREDENTIALS --> PASSWORD_VERIFY
    MFA_TOKEN --> MFA_VERIFY
    
    USERNAME_CHECK --> ACCOUNT_STATUS
    PASSWORD_VERIFY --> ACCOUNT_STATUS
    MFA_VERIFY --> ACCOUNT_STATUS
    
    ACCOUNT_STATUS --> JWT_CREATION
    JWT_CREATION --> REFRESH_TOKEN
    REFRESH_TOKEN --> TOKEN_SIGNING
    TOKEN_SIGNING --> SESSION_CREATION
    
    %% Security flow
    LOGIN_REQUEST --> RATE_LIMITING
    PASSWORD_VERIFY --> BRUTE_FORCE
    ACCOUNT_STATUS --> AUDIT_LOG
    SESSION_CREATION --> SECURITY_ALERT
    
    %% Response flow
    TOKEN_SIGNING --> TOKEN_RESPONSE
    SESSION_CREATION --> USER_PROFILE
    USER_PROFILE --> PERMISSIONS
    PERMISSIONS --> RESPONSE_HEADERS
    
    %% Session management
    SESSION_CREATION --> SESSION_STORAGE
    SESSION_STORAGE --> SESSION_TRACKING
    SESSION_TRACKING --> SESSION_TIMEOUT
    SESSION_TIMEOUT --> LOGOUT_HANDLER
    
    %% Styling
    classDef request fill:#e3f2fd
    classDef validation fill:#f1f8e9
    classDef token fill:#e8f5e8
    classDef security fill:#ffebee
    classDef response fill:#fff3e0
    classDef session fill:#f3e5f5
    
    class LOGIN_REQUEST,CREDENTIALS,MFA_TOKEN request
    class USERNAME_CHECK,PASSWORD_VERIFY,MFA_VERIFY,ACCOUNT_STATUS validation
    class JWT_CREATION,REFRESH_TOKEN,TOKEN_SIGNING,SESSION_CREATION token
    class RATE_LIMITING,BRUTE_FORCE,AUDIT_LOG,SECURITY_ALERT security
    class TOKEN_RESPONSE,USER_PROFILE,PERMISSIONS,RESPONSE_HEADERS response
    class SESSION_STORAGE,SESSION_TRACKING,SESSION_TIMEOUT,LOGOUT_HANDLER session
```

## 📊 Data Export API Flow

```mermaid
graph LR
    subgraph "Export Request"
        CLIENT_REQUEST[Client Request]
        FORMAT_SELECTION[Format Selection]
        FILTER_CRITERIA[Filter Criteria]
        DATE_RANGE[Date Range]
    end
    
    subgraph "Request Processing"
        VALIDATION[Request Validation]
        AUTHORIZATION[Authorization Check]
        QUOTA_CHECK[Quota Verification]
        JOB_CREATION[Export Job Creation]
    end
    
    subgraph "Data Preparation"
        QUERY_BUILDER[Query Builder]
        DATA_RETRIEVAL[Data Retrieval]
        DATA_FILTERING[Data Filtering]
        DATA_TRANSFORMATION[Data Transformation]
    end
    
    subgraph "Format Processing"
        CSV_FORMATTER[CSV Formatter]
        JSON_FORMATTER[JSON Formatter]
        XML_FORMATTER[XML Formatter]
        EXCEL_FORMATTER[Excel Formatter]
    end
    
    subgraph "File Generation"
        FILE_CREATION[File Creation]
        COMPRESSION[File Compression]
        ENCRYPTION[File Encryption]
        STORAGE[Temporary Storage]
    end
    
    subgraph "Delivery Options"
        DIRECT_DOWNLOAD[Direct Download]
        EMAIL_DELIVERY[Email Delivery]
        API_RESPONSE[API Response]
        WEBHOOK_NOTIFICATION[Webhook Notification]
    end
    
    %% Flow connections
    CLIENT_REQUEST --> VALIDATION
    FORMAT_SELECTION --> AUTHORIZATION
    FILTER_CRITERIA --> QUOTA_CHECK
    DATE_RANGE --> JOB_CREATION
    
    VALIDATION --> QUERY_BUILDER
    AUTHORIZATION --> DATA_RETRIEVAL
    QUOTA_CHECK --> DATA_FILTERING
    JOB_CREATION --> DATA_TRANSFORMATION
    
    DATA_RETRIEVAL --> CSV_FORMATTER
    DATA_FILTERING --> JSON_FORMATTER
    DATA_TRANSFORMATION --> XML_FORMATTER
    QUERY_BUILDER --> EXCEL_FORMATTER
    
    CSV_FORMATTER --> FILE_CREATION
    JSON_FORMATTER --> COMPRESSION
    XML_FORMATTER --> ENCRYPTION
    EXCEL_FORMATTER --> STORAGE
    
    FILE_CREATION --> DIRECT_DOWNLOAD
    COMPRESSION --> EMAIL_DELIVERY
    ENCRYPTION --> API_RESPONSE
    STORAGE --> WEBHOOK_NOTIFICATION
    
    %% Styling
    classDef request fill:#e3f2fd
    classDef processing fill:#f1f8e9
    classDef preparation fill:#e8f5e8
    classDef formatting fill:#fff3e0
    classDef generation fill:#f3e5f5
    classDef delivery fill:#fce4ec
    
    class CLIENT_REQUEST,FORMAT_SELECTION,FILTER_CRITERIA,DATE_RANGE request
    class VALIDATION,AUTHORIZATION,QUOTA_CHECK,JOB_CREATION processing
    class QUERY_BUILDER,DATA_RETRIEVAL,DATA_FILTERING,DATA_TRANSFORMATION preparation
    class CSV_FORMATTER,JSON_FORMATTER,XML_FORMATTER,EXCEL_FORMATTER formatting
    class FILE_CREATION,COMPRESSION,ENCRYPTION,STORAGE generation
    class DIRECT_DOWNLOAD,EMAIL_DELIVERY,API_RESPONSE,WEBHOOK_NOTIFICATION delivery
```

## 🔄 Background Job API Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant JobQueue
    participant Worker
    participant Database
    participant Notifier
    
    Note over Client,Notifier: Job Submission
    Client->>API: Submit background job
    API->>API: Validate request
    API->>JobQueue: Queue job
    JobQueue->>API: Job ID
    API->>Client: Job submitted (ID: 123)
    
    Note over Client,Notifier: Job Processing
    JobQueue->>Worker: Assign job
    Worker->>Database: Start processing
    Worker->>JobQueue: Update status (RUNNING)
    
    Note over Client,Notifier: Progress Updates
    loop Every 30 seconds
        Worker->>Database: Update progress
        Database->>Notifier: Progress event
        Notifier->>Client: Progress notification
    end
    
    Note over Client,Notifier: Job Completion
    Worker->>Database: Complete processing
    Worker->>JobQueue: Update status (COMPLETED)
    JobQueue->>Notifier: Job complete event
    Notifier->>Client: Completion notification
    
    Note over Client,Notifier: Result Retrieval
    Client->>API: Get job results (ID: 123)
    API->>Database: Fetch results
    Database->>API: Results data
    API->>Client: Return results
    
    Note over Client,Notifier: Error Handling
    alt Job fails
        Worker->>Database: Log error
        Worker->>JobQueue: Update status (FAILED)
        JobQueue->>Notifier: Job failed event
        Notifier->>Client: Error notification
    end
    
    Note over Client,Notifier: Cleanup
    Client->>API: Acknowledge completion
    API->>JobQueue: Mark for cleanup
    JobQueue->>Database: Archive job data
```
