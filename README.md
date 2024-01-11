<h1> Chat Web </h1>

<p1>This project is a simple web chat application developed with FastAPI and WebSockets. The main goal is to provide a real-time chat experience for users, where they can connect, send messages, and interact instantly.</p1>

<h3>Key Features</h3>
<p1> FastAPI: We used FastAPI as the web framework to build the application quickly, efficiently and asynchronously.</p1><br><br>
<p1>WebSockets: We implemented real-time chat functionality using WebSockets, allowing two-way communication between the server and clients.</p1><br><br>
<p1> Connection Management: We have implemented a robust system to manage user connections, controlling chat entry and exit in a secure manner.</p1><br><br>
<p1>Private messaging: Users have the ability to send private messages to each other, creating a more personalized chat experience.</p1><br><br>
<p1>User Validation: We have implemented user validation to ensure that usernames have the correct format and are unique.</p1><br><br>


<h3>How to Run</h3><br>

      pip install -r requirements.txt

<br> 
      
       uvicorn main:app --reload


<br>
Open your browser http://127.0.0.1:8000
