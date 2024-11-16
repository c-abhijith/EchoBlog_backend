# EchoBlog Backend API

A FastAPI-based backend for a blogging platform with user authentication, blog management, and social features.

## Features

### Authentication
- User signup and login
- JWT token-based authentication
- Role-based authorization (User/Admin)

### User Management
- Profile management (bio, title, social links)
- Profile image upload
- View user profiles and their blogs

### Blog Management
- Create, read, update, and delete blogs
- Image upload for blog posts
- Like/unlike functionality
- Comment system
- View blog statistics (likes, comments)

### Comments
- Add comments to blogs
- Edit own comments
- Delete comments (owner/admin)
- View all comments on a blog

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **Image Storage**: Cloudinary
- **Documentation**: Swagger/OpenAPI

## API Endpoints

### Authentication
- `POST /auth/signup`: Register new user
- `POST /auth/login`: User login

### User Routes
- `GET /users/profile`: Get own profile
- `GET /users/{user_id}`: Get user profile
- `PUT /users/profile`: Update profile
- `PATCH /users/profile/image`: Update profile image

### Blog Routes
- `POST /blogs/`: Create new blog
- `GET /blogs/`: List all blogs
- `GET /blogs/{blog_id}`: Get single blog
- `PUT /blogs/{blog_id}`: Update blog
- `DELETE /blogs/{blog_id}`: Delete blog
- `PATCH /blogs/{blog_id}/like`: Like/unlike blog

### Comment Routes
- `POST /blogs/{blog_id}/comments/`: Add comment
- `GET /blogs/{blog_id}/comments/`: List comments
- `PUT /blogs/{blog_id}/comments/{comment_id}`: Update comment
- `DELETE /blogs/{blog_id}/comments/{comment_id}`: Delete comment

## Setup

1. Clone the repository: 