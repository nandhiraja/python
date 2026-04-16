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
    else if(data.type==='chat-history'){
        console.log('displaying history...')
        document.getElementById('chat-area').innerHTML='';

        data.history.forEach(message=>{
            displayMessage(message)
        })
    }
    else if (data.type === 'chat-message' && data.user!=currentUser) {
       
         displayMessage(data);
      
        
    }
    };

    }

})

function addRoomEventListener(){
    let roomsList = document.querySelectorAll('.room')

    roomsList.forEach(room=>{
        room.addEventListener('click',(e)=>{
            let roomId = e.target.dataset.roomId
            console.log("Room clicked", roomId)
            let message = {
                type:"chat-history",
                user: currentUser,
                room:roomId   
            }
            ws.send(JSON.stringify(message))
        })
    })
}


const sendMessage = () => {
    const text = input.value;
    if (text.trim() === "") return;
    let currentUser = login.value
    if (currentUser=='login'){
        return
    }

    

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
    const isMe = data.user===currentUser
    const msgHtml = `
        <div class="${isMe? 'sender':'receiver'} message">
            <p style='color:black'>${isMe? '':data.user+': '}</p> ${data.text}
            <div class="${'receiver-time'} timestamp">${data.timestamp}</div>
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
    addRoomEventListener()
}