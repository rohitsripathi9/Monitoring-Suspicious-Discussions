create database c2r2db;

use c2r2db;

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE,
    email_id VARCHAR(40) UNIQUE,
    user_status VARCHAR(10) DEFAULT 'good',
    user_score INT,
    user_password varchar(100)
)  AUTO_INCREMENT=1000;

CREATE TABLE admins (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    admin_name VARCHAR(50),
    admin_email VARCHAR(50),
    admin_password VARCHAR(100)
)  AUTO_INCREMENT=2000;

CREATE TABLE posts (
    post_id INT PRIMARY KEY AUTO_INCREMENT,
    post_content VARCHAR(1000),
    poster_id INT,
    post_status VARCHAR(10),
    post_score INT,
    admin_id INT,
    FOREIGN KEY (admin_id)
        REFERENCES admins (admin_id)
);

show tables;

select * from posts;
select * from users;
select * from admins;
select * from requests_processed;
select * from words;