# Project Nexus: Job Portal For Recruiters and Talents

# Project Nexus: Advanced Job Portal Backend

## Overview

**Project Nexus** is a sophisticated, enterprise-grade job portal backend that revolutionizes career development through intelligent matching, real-time features, and comprehensive user management. Built with modern Django architecture, this platform goes beyond traditional job boards by providing AI-powered skill matching, personalized recommendations, and seamless user experiences for both job seekers and recruiters.

## Key Features

### Core Functionality
- **Multi-Role User Management:** Comprehensive user system supporting job seekers, recruiters, and companies with role-based access control
- **Advanced Job Management:** Full CRUD operations for job postings with categories, salary ranges, and location-based filtering
- **Intelligent Application System:** Complete application workflow with status tracking, resume attachments, and automated notifications
- **Company Profiles:** Detailed company management with promotion capabilities and job posting rights

### Advanced Features
- **AI-Powered Skill Matching:** Sophisticated algorithm that analyzes user skills against job requirements with compatibility scoring
- **Personalized Job Recommendations:** Machine learning-driven suggestions based on user profiles, skills, and interaction history
- **Real-Time Notifications:** Multi-channel notification system (in-app, email, push) with user preference management
- **Dynamic Activity Feed:** Personalized feed showing relevant job postings, company updates, and promotional content
- **File Upload System:** Secure file handling for resumes, cover letters, certificates, and profile images with validation
- **Promotion Engine:** Advanced promotion system for jobs, companies, and talent profiles with package management

### Security & Performance
- **JWT Authentication:** Secure token-based authentication with refresh token rotation and blacklisting
- **Multi-Factor Authentication (MFA):** TOTP-based two-factor authentication for enhanced security
- **Rate Limiting:** Intelligent throttling system with different limits for various operations
- **Redis Caching:** High-performance caching layer for frequently accessed data and session management
- **Background Processing:** Celery-based asynchronous task processing for heavy operations
- **CORS & Security Headers:** Comprehensive security configuration for production deployment

## Modular Architecture

The application follows a clean, modular Django architecture with 11 specialized apps, each handling specific business domains:

### Core Applications

**Core (`core/`)**
- Base models, mixins, and utilities shared across the application
- Custom pagination, permissions, and response handling
- Exception handling and middleware for request tracking
- Centralized configuration and shared functionality

**API (`api/`)**
- Central API routing and authentication endpoints
- JWT token management (login, refresh, logout)
- User registration and authentication flows
- API versioning and endpoint organization

**User (`user/`)**
- User model with roles (Talent, Recruiter, Company)
- Profile management and email verification
- Admin interfaces and user management
- MFA integration and security features

### Business Domain Applications

**Job (`job/`)**
- Job posting and management system
- Job categories and search functionality
- Advanced filtering and search capabilities
- Job promotion and visibility controls

**Company (`company/`)**
- Company profile management
- Company verification and branding
- Job posting permissions and management
- Company promotion and marketing features

**Application (`application/`)**
- Job application workflow and tracking
- Application status management (Pending, Reviewed, Accepted, Rejected)
- Resume and document attachment handling
- Application analytics and reporting

**Skill (`skill/`)**
- Skill database and categorization
- User skill profiles with proficiency levels
- AI-powered skill matching algorithm
- Job recommendation engine with caching
- Background task processing for heavy computations

**Address (`address/`)**
- Geographic data management (Countries, States, Cities)
- Location-based job filtering
- Address lookup and validation services
- Geographic search capabilities

### Supporting Applications

**Upload (`upload/`)**
- Secure file upload and management
- File type validation and size limits
- Thumbnail generation for images
- Generic file attachment system

**Notification (`notification/`)**
- Multi-channel notification system
- User notification preferences
- Email, in-app, and push notification support
- Notification scheduling and delivery tracking

**Feed (`feed/`)**
- Personalized activity feed generation
- Content aggregation and scoring
- Real-time feed updates
- User engagement tracking

**Promotion (`promotion/`)**
- Advanced promotion and advertising system
- Promotion packages and pricing
- Content promotion (jobs, companies, profiles)
- Promotion analytics and performance tracking

## Technical Stack

### Backend Technologies
- **Python 3.13:** Core programming language
- **Django 5.2:** Web framework with REST API capabilities
- **Django REST Framework:** API development and serialization
- **PostgreSQL:** Primary relational database with optimized indexing
- **Redis:** High-performance caching and session storage
- **Celery:** Asynchronous task processing and background jobs
- **RabbitMQ:** Message broker for task queue management

### Security & Authentication
- **JWT (JSON Web Tokens):** Stateless authentication with refresh tokens
- **Multi-Factor Authentication:** TOTP-based 2FA integration
- **Rate Limiting:** Intelligent throttling (1000/hour users, 100/hour anonymous)
- **CORS Configuration:** Secure cross-origin resource sharing
- **Security Headers:** Comprehensive security middleware stack

### Development & Deployment
- **Docker & Docker Compose:** Containerized development and production
- **GitHub Actions:** Automated CI/CD pipeline
- **Swagger/OpenAPI:** Comprehensive API documentation
- **Pytest:** Testing framework with comprehensive test coverage
- **WhiteNoise:** Static file serving for production

## Performance Optimizations

### Caching Strategy
- **Redis Integration:** Multi-level caching for job recommendations, skill profiles, and user sessions
- **Query Optimization:** Database indexing and query optimization for fast data retrieval
- **Background Processing:** Heavy computations moved to Celery tasks for improved response times
- **CDN Ready:** Static file serving optimized for production deployment

### Scalability Features
- **Horizontal Scaling:** Stateless design allows for easy horizontal scaling
- **Database Optimization:** Proper indexing and connection pooling for high-traffic scenarios
- **Asynchronous Processing:** Non-blocking operations for better resource utilization
- **Rate Limiting:** Intelligent throttling prevents system overload

## API Documentation

The API is fully documented using **Swagger/OpenAPI 3.0** with comprehensive endpoint documentation, request/response schemas, and interactive testing capabilities.

### Key API Endpoints
- **Authentication:** `/api/auth/` - User registration, login, logout, and token management
- **Users:** `/api/users/` - User profile management and role-based operations
- **Jobs:** `/api/jobs/` - Job posting, searching, and management
- **Skills:** `/api/skills/` - Skill management and matching algorithms
- **Applications:** `/api/applications/` - Job application workflow
- **Companies:** `/api/companies/` - Company profile and job management
- **Notifications:** `/api/notifications/` - Real-time notification system
- **Feed:** `/api/feed/` - Personalized activity feed
- **Uploads:** `/api/uploads/` - File upload and management

### Interactive Documentation
Access the interactive API documentation at:
- **Swagger UI:** `http://localhost:8000/api/docs/`
- **ReDoc:** `http://localhost:8000/api/redoc/`

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation & Setup

1. **Clone the repository:**
    ```bash
   git clone https://github.com/chinazagideon/alx-project-nexus.git
    cd alx-project-nexus
    ```

2. **Environment Configuration:**
    ```bash
    cp .env.example .env
   # Edit .env with your specific configurations
    ```

3. **Start the application:**
    ```bash
    docker-compose up --build
    ```

4. **Access the application:**
   - **API Documentation:** http://localhost:8000/api/docs/
   - **Admin Panel:** http://localhost:8000/admin/
   - **Health Check:** http://localhost:8000/health/

### Development Setup

For local development without Docker:

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database setup:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Run development server:**
   ```bash
   python manage.py runserver
   ```

## Advanced Features Deep Dive

### Skill Matching Algorithm
The application features a sophisticated skill matching system that:
- Analyzes user skill profiles with proficiency levels (Beginner to Expert)
- Compares against job requirements with importance weighting
- Provides compatibility scores and detailed match analysis
- Uses background processing for performance optimization
- Implements intelligent caching for fast response times

### Notification System
Comprehensive notification management including:
- Multi-channel delivery (in-app, email, push notifications)
- User preference management and quiet hours
- Event-driven notifications for applications, job matches, and promotions
- Deduplication and delivery tracking
- Scheduled and real-time notification support

### Promotion Engine
Advanced promotion system featuring:
- Flexible promotion packages with pricing tiers
- Content promotion for jobs, companies, and talent profiles
- Placement targeting (feed, homepage, listings)
- Promotion analytics and performance tracking
- Automated promotion lifecycle management

## Development Best Practices

### Code Quality
- **Modular Design:** Clean separation of concerns with 11 specialized Django apps
- **Type Hints:** Comprehensive type annotations for better code maintainability
- **Documentation:** Extensive API documentation with Swagger/OpenAPI
- **Testing:** Comprehensive test coverage with pytest framework
- **Code Standards:** PEP 8 compliance and consistent code formatting

### Security Implementation
- **Authentication:** JWT-based stateless authentication with refresh tokens
- **Authorization:** Role-based access control with granular permissions
- **Data Protection:** Input validation, SQL injection prevention, and XSS protection
- **Rate Limiting:** Intelligent throttling to prevent abuse and ensure fair usage
- **CORS Configuration:** Secure cross-origin resource sharing setup

### Performance Optimization
- **Caching Strategy:** Multi-level Redis caching for frequently accessed data
- **Database Optimization:** Proper indexing and query optimization
- **Background Processing:** Celery tasks for heavy computations
- **Static File Serving:** Optimized static file delivery with WhiteNoise
- **Connection Pooling:** Efficient database connection management

### Challenges Faced & Solutions Implemented

#### 1. **Feed System Architecture Challenge**
**Challenge:** Building a scalable, real-time activity feed that aggregates content from multiple sources (jobs, companies, promotions) while maintaining performance and providing personalized content to users.

**Solution Implemented:**
- **Generic Foreign Key Architecture:** Created a unified `FeedItem` model using Django's `GenericForeignKey` to reference any content type (jobs, companies, promotions) without tight coupling
- **Redis-based Cursor Pagination:** Implemented `zpage_by_cursor()` using Redis sorted sets for efficient, cursor-based pagination that scales with large datasets
- **Event-driven Feed Population:** Built signal handlers that automatically create feed items when jobs are posted, companies join, or promotions become active
- **Scoring Algorithm:** Developed a time-decay scoring system that prioritizes recent content while maintaining relevance
- **Performance Optimization:** Added database indexes on `[-score, id]`, `[content_type, object_id]`, and `[event_type, is_active]` for fast querying
- **Management Commands:** Created `rebuild_feed` and `prune_feed` commands for maintenance and data integrity

```python
# Key implementation in feed/models.py
class FeedItem(models.Model):
    event_type = models.CharField(max_length=50, choices=EVENT_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    score = models.DecimalField(max_digits=20, decimal_places=6)
    is_active = models.BooleanField(default=True)
```

#### 2. **Entity Relationship Management Challenge**
**Challenge:** Managing complex relationships between standalone Django apps (user, job, company, application, skill) while maintaining data integrity and avoiding circular dependencies.

**Solution Implemented:**
- **Centralized Core App:** Created a `core` app with shared models, mixins, and utilities that other apps can import without circular dependencies
- **Generic Foreign Key Pattern:** Used `GenericForeignKey` for flexible relationships (e.g., promotions can target any content type)
- **Django Settings Integration:** Leveraged `settings.AUTH_USER_MODEL` and custom model references to avoid hardcoded imports
- **Signal-based Communication:** Implemented Django signals for loose coupling between apps (e.g., job creation triggers feed updates)
- **Custom Permission Classes:** Created reusable permission classes in `core.permissions_enhanced` that can be shared across apps
- **Dependency Management:** Carefully ordered app dependencies in `INSTALLED_APPS` and migration dependencies

```python
# Example of cross-app relationship in application/models.py
class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)  # job app
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # user app
    resume = models.ForeignKey(UPLOAD_MODEL, on_delete=models.CASCADE)  # upload app
```

#### 3. **Search Query Optimization Challenge**
**Challenge:** Building a high-performance search system that can handle complex queries across multiple fields while maintaining sub-second response times and supporting advanced filtering.

**Solution Implemented:**
- **Dual Search Strategy:** Implemented both PostgreSQL full-text search (for production) and Django ORM search (for development) with automatic detection
- **Database Indexing:** Created comprehensive database indexes including GIN indexes for full-text search vectors
- **Query Optimization:** Used `select_related()` and `prefetch_related()` to minimize database hits
- **Caching Layer:** Implemented Redis caching for search results with intelligent cache invalidation
- **Permission-aware Filtering:** Integrated user-based permission filtering directly into search queries
- **Background Indexing:** Created management commands for building and maintaining search indexes
- **Search Vector Optimization:** Built custom search vectors that combine title, description, company name, and location fields

```python
# Key optimization in job/search_service.py
def _postgresql_search(self, queryset, query: str):
    search_vector = SearchVector('title', 'description', 'company__name', 'city__name')
    search_query = SearchQuery(query)
    return queryset.annotate(
        search=search_vector,
        rank=SearchRank(search_vector, search_query)
    ).filter(search=search_query).order_by('-rank', '-is_promoted', '-promotion_priority')
```

#### 4. **Skill Matching Performance Challenge**
**Challenge:** Creating an intelligent skill matching algorithm that can process thousands of user-job combinations in real-time while providing accurate compatibility scores.

**Solution Implemented:**
- **Asynchronous Processing:** Moved heavy skill matching calculations to Celery background tasks to prevent UI blocking
- **Intelligent Caching:** Implemented multi-level caching (5-10 minute TTL) for recommendations and skill profiles
- **Proficiency-based Scoring:** Developed a sophisticated scoring algorithm that considers user proficiency levels, job requirements, and skill importance weights
- **Rate Limiting:** Applied custom throttling (10 requests/minute) for expensive skill matching operations
- **Precomputation Strategy:** Built background tasks to precompute recommendations for active users
- **Database Optimization:** Used `select_related()` and efficient queries to minimize database load

```python
# Performance optimization in skill/services.py
@classmethod
def get_user_skill_match_percentage(cls, user_skills: List[Dict], job_skills: List[Dict]) -> float:
    user_skill_ids = {skill['skill_id'] for skill in user_skills}
    job_skill_ids = {skill['skill_id'] for skill in job_skills}
    exact_matches = len(user_skill_ids.intersection(job_skill_ids))
    return round((exact_matches / len(job_skill_ids)) * 100, 2)
```

#### 5. **Permission System Security Challenge**
**Challenge:** Implementing a robust, role-based permission system that prevents unauthorized access while maintaining performance and code maintainability.

**Solution Implemented:**
- **Custom Permission Classes:** Created granular permission classes (`IsJobOwnerOrStaff`, `IsRecruiterOrAdmin`, etc.) for different resource types
- **Centralized Permission Logic:** Built reusable permission and queryset methods in `core.viewset_permissions` to avoid code duplication
- **Role-based Access Control:** Implemented comprehensive RBAC with different access levels for admin, recruiter, and talent roles
- **Object-level Permissions:** Ensured users can only access resources they own or have permission to view
- **Search Integration:** Applied permission filtering directly in search services to prevent data leakage
- **Audit Trail:** Maintained clear permission boundaries with comprehensive logging and error handling


## Best Practices & Personal Takeaways

### **Architecture & Design Patterns**
* **Modular Django Architecture:** Successfully implemented a clean, 11-app Django architecture where each app has a single responsibility, making the codebase maintainable and scalable
* **Generic Foreign Key Pattern:** Mastered the use of `GenericForeignKey` for flexible, loosely-coupled relationships between different content types, enabling the feed system and promotion engine
* **Signal-based Communication:** Implemented Django signals for loose coupling between apps, allowing changes in one app to trigger actions in another without direct dependencies
* **Centralized Core Utilities:** Created a `core` app with shared models, mixins, and utilities that other apps can import, preventing code duplication and circular dependencies

### **Performance & Scalability**
* **Multi-level Caching Strategy:** Implemented intelligent Redis caching with different TTLs for different data types (5-10 minutes for dynamic content, longer for static data)
* **Database Query Optimization:** Mastered the use of `select_related()`, `prefetch_related()`, and database indexing to minimize query count and improve response times
* **Asynchronous Task Processing:** Successfully integrated Celery for background processing of heavy operations like skill matching and recommendation generation
* **Cursor-based Pagination:** Implemented efficient cursor pagination using Redis sorted sets for the feed system, enabling infinite scrolling without performance degradation

### **Security & Data Integrity**
* **Role-based Access Control (RBAC):** Implemented comprehensive permission system with granular access control for different user roles (admin, recruiter, talent)
* **Object-level Permissions:** Ensured users can only access resources they own or have permission to view, preventing unauthorized data access
* **Permission-aware Search:** Integrated permission filtering directly into search services to prevent data leakage through search endpoints
* **Input Validation & Sanitization:** Implemented comprehensive input validation using Django serializers and custom validation logic

### **Code Quality & Maintainability**
* **Type Hints & Documentation:** Used comprehensive type hints throughout the codebase and maintained detailed docstrings for all classes and methods
* **Custom Permission Classes:** Created reusable, well-documented permission classes that can be shared across different viewsets
* **Management Commands:** Built custom Django management commands for data maintenance, seeding, and system administration
* **Comprehensive Testing:** Implemented thorough testing strategies including unit tests, integration tests, and API endpoint testing

### **Problem-Solving & Learning**
* **Breaking Down Complex Problems:** Learned to decompose complex features (like the feed system) into smaller, manageable components that can be built and tested independently
* **Performance Profiling:** Developed skills in identifying performance bottlenecks and implementing targeted optimizations (database indexing, query optimization, caching)
* **Technology Integration:** Successfully integrated multiple technologies (Django, Redis, Celery, PostgreSQL) while maintaining clean architecture and avoiding vendor lock-in
* **Iterative Development:** Adopted an iterative approach to building complex features, starting with basic functionality and gradually adding advanced features and optimizations

### **Professional Development Practices**
* **Version Control Mastery:** Leveraged Git and GitHub for proper version control, branching strategies, and collaborative development
* **API Documentation:** Implemented comprehensive API documentation using Swagger/OpenAPI with interactive testing capabilities
* **Docker Containerization:** Used Docker and Docker Compose for consistent development and deployment environments
* **Monitoring & Logging:** Implemented proper logging and error handling throughout the application for better debugging and monitoring

## Mentors & Acknowledgements

A huge thank you to my mentors: **Cole, Faith, and Amanuel**, for their invaluable guidance and feedback throughout the program. Their support was instrumental in the successful completion of this project.

## Project Timeline

- **Development Phase:** 12 weeks intensive development
- **Technology Stack:** Modern Python/Django ecosystem with enterprise-grade tools
- **Deployment:** Production-ready with Docker containerization and CI/CD pipeline

