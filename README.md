## Application architecture

![image](https://github.com/docker/getting-started-todo-app/assets/313480/c128b8e4-366f-4b6f-ad73-08e6652b7c4d)


This sample application is a simple React frontend that receives data from a
Node.js backend. 

When the application is packaged and shipped, the frontend is compiled into
static HTML, CSS, and JS and then bundled with the backend where it is then
served as static assets. So no... there is no server-side rendering going on
with this sample app.

During development, since the backend and frontend need different dev tools, 
they are split into two separate services. This allows [Vite](https://vitejs.dev/) 
to manage the React app while [nodemon](https://nodemon.io/) works with the 
backend. With containers, it's easy to separate the development needs!
