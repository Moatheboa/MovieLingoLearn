DROP TABLE IF EXISTS user_scene_tracking;
DROP TABLE IF EXISTS available_subs;
DROP TABLE IF EXISTS subtitles;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS movies;

CREATE TABLE movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL
);

CREATE TABLE available_subs (
    movie_id INT REFERENCES movies(id),
    language VARCHAR(5) NOT NULL,

    PRIMARY KEY (movie_id, language)
);

CREATE TABLE subtitles (
    movie_id INT REFERENCES movies(id),
    movie_scene INT,
    language VARCHAR(5),
    subtitle VARCHAR(400),

    PRIMARY KEY (movie_id, movie_scene, language)
);

CREATE TABLE users (
    username VARCHAR(20) PRIMARY KEY,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE user_scene_tracking (
    username VARCHAR(20) REFERENCES users(username),
    movie_id INT REFERENCES movies(id),
    current_scene INT,

    PRIMARY KEY (username, movie_id)
)