# PeerJot
video demo: https://youtu.be/iNlQ7GLOKTU
#### Description:
PeerJot is a note taking app that helps better structure notes. 
Created with Python, Flask, and Postgresql / SQLAlchemy


# Features
- users can add notes with a main title and sub title.
- users can create a page that is associated with a note.
- Once a page is created that is where the structure of the note can be created.
- There is an Edit and delete button features to get rid of notes, pages, blocks of notes, bookmarks, and sidenotes.

  # Structure of the note page
  - Bookmarks
  - Sidenotes
  - Note blocks
  - Note blocks and bookmarks can be viewed in a full page view where it is all put together from those sections and can be printed.
 
 # design choices
 I wanted to keep the design and overall usage simple and user friendly. So I picked light colors with dark text.
 I do think a to improve this project in the future a better layout could improve this project better. Currently there is a page for the notes section and a page 
 for the note page section. One example would be to create a fixed side nav of the page title and when you click 
 on a page title the note building section pops up on the same page side by side instead of adding extra linking and navigation to anothe page.

 # Recap
 - Some of the challenges I encountered was setting up the Postgres database with the difference tables to add and what information to group together to created each feature.
 - Learning how I wanted the page routing was a difficult process to because if it didnt flow correctly or seemed off then other parts of the project just wouldn't fit together right.
 - I used SQLAlchemy with Postgresql so understanding how to set up the database models took some time to understand due to adding foreign keys to associated tables.
 - Although I did gain knowledge in using SQL queries. I did use the SQLAlchemy way of writing SQL queries. One way to also refactor this project is go back and use raw sql commands.
    
