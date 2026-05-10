CREATE DATABASE EcommerceDB;
GO

USE EcommerceDB;
GO

CREATE TABLE Products (
    ProductID INT PRIMARY KEY,
    Title NVARCHAR(255),
    Price DECIMAL(10, 2),
    Description NVARCHAR(MAX),
    Category NVARCHAR(100),
    ImageURL NVARCHAR(MAX)
);

CREATE TABLE Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    FullName NVARCHAR(100),
    Email NVARCHAR(255) UNIQUE,
    PasswordHash NVARCHAR(255),
    CreatedAt DATETIME DEFAULT GETDATE()
);