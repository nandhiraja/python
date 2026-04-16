let input = document.getElementById('user-input')
let sendBtn = document.getElementById('send-btn')
let login =  document.getElementById('user-id')
let currentRoom = 'general'; 
let ws =  null
let currentUser=null
let joinBtn = document.getElementById('room-join-btn')
let availableRooms = []

login.addEventListener('change',()=>{
    console.log('login : ', login.value)
    
    currentUser = login.value
   
    if (currentUser!='login'){
        if(currentUser=='ragu'){
        receiver='Nandhiraja'
        }
        else{
          receiver = 'ragu'  
        }
        if(ws){
        console.log('Connection closed: ',currentUser)
        ws.close()
    }
     console.log('new Connection : ',currentUser)

    ws =  new WebSocket(`ws://localhost:8080/ws/${currentUser}`)

    ws.onopen=()=>{
        const messageData = {
        type: 'initial-data',
        user: currentUser,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            };

    ws.send(JSON.stringify(messageData));
    }
    
    ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    console.log("Socket_data : ",data)
    if(data.type =='available-rooms'){
        console.log('got avilable rooms')
        availableRooms= data.availableRooms
        updateRooms()
    }
    else if (data.type === 'chat-message') {
        displayMessage(data);
    }
    };

    }

})
const sendMessage = () => {
    const text = input.value;
    if (text.trim() === "") return;
    let currentUser = login.value
    if (currentUser=='login'){
        return
    }

    const chatArea = document.getElementById('chat-area');
    
    const msgHtml = `
        <div class="${'sender'} message">
            <strong>${'You'}:</strong> ${text}
            <div class="${'receiver-time'} timestamp">${ new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
        </div>
    `;
    chatArea.innerHTML += msgHtml;
    chatArea.scrollTop = chatArea.scrollHeight;

    const messageData = {
        type: 'chat-message',
        room: currentRoom,
        user: currentUser,
        message: text,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    ws.send(JSON.stringify(messageData));
    input.value = "";
};

sendBtn.addEventListener('click', sendMessage);



function displayMessage(data) {
    const chatArea = document.getElementById('chat-area');
    
    const msgHtml = `
        <div class="${'receiver'} message">
            <strong>${data.user}:</strong> ${data.text}
            <div class="${'sender-time'} timestamp">${data.timestamp}</div>
        </div>
    `;
    chatArea.innerHTML += msgHtml;
    chatArea.scrollTop = chatArea.scrollHeight; 
}

joinBtn.addEventListener('click',()=>{
    let joinRoom = document.getElementById('room-join-input')
    console.log(joinRoom.value)
    let message = {
        type:'room-join',
        user:currentUser,
        room:currentRoom

    }
    ws.send(JSON.stringify(message));

    
})

function updateRooms(){
    let roomArea = document.querySelector('.room-area');
    roomArea.innerHTML=''

    availableRooms.forEach(room=>{
        let div = document.createElement('div')
        div.classList.add('room')
        div.dataset.roomId=room
        div.innerText=room
        roomArea.appendChild(div)
        
    })
}