// let a = 0;
let id = -1;
let options = [];

const getOptions = async (id) => {
    const response = await fetch(`http://127.0.0.1:5000/api/modules/${id}`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
    });
    let data = await response.json();
    console.log(data.data);
    var str = ""
    for (var item of data.data) {
        str += `<option value=${item.module_id}>` + item.module_title + "</option>"
    }
    document.getElementById('select-module').innerHTML = str;
    // if(data.id!=-1) {
    //     login();
    //     chrome.storage.sync.set({'id': data.id}, ()=> {
    //         console.log("Done");
    //     })
    // }
}

const login = (id) => {
    document.getElementById('login-form').style.display = "none";
    document.getElementById('main').style.display = "block";
    getOptions(id);
}

const logout = () => {
    document.getElementById('login-form').style.display = "block";
    document.getElementById('main').style.display = "none";
    chrome.storage.sync.set({'id': -1}, ()=> {
        console.log("Done");
    })
}
chrome.storage.sync.get("id", function(result) {
    if(result.id==undefined) {
        console.log("here");
        logout();
    }
    else if(result.id==-1) {
        logout();
    }
    else {
        id = result.id;
        login(id);
    }
});
// document.getElementById("btn").addEventListener('click', () => {
//     document.getElementById("display").innerHTML = ++a;
//     chrome.storage.sync.set({'a': a}, ()=> {
//         console.log(a);
//     })
    
// })

const getToken = async (username, password) => {
    const response = await fetch(`http://127.0.0.1:5000/api/login/${username}/${password}`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
    });
    let data = await response.json();
    console.log(data.id);
    if(data.id!=-1) {
        login();
        chrome.storage.sync.set({'id': data.id}, ()=> {
            console.log("Done");
        })
    }
}

document.getElementById("submit-login").addEventListener('click', () => {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    getToken(username, password);
})

document.getElementById("logout").addEventListener('click', () => {
    logout();
});


const addPdf = async (id, module_id, url) => {
    const response = await fetch(`http://127.0.0.1:5000/api/pdf`, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "module_id": module_id,
            "url": url
        }),
    });
    console.log(response);
}

const addImage = async (id, module_id, url) => {
    const response = await fetch(`http://127.0.0.1:5000/api/image`, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "module_id": module_id,
            "url": url
        }),
    });
    console.log(response);
}

const addVideo = async (id, module_id, url) => {
    const response = await fetch(`http://127.0.0.1:5000/api/video`, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "module_id": module_id,
            "url": url
        }),
    });
    console.log(response);
}

document.getElementById("add").addEventListener('click', () => {
    const module_id = document.getElementById('select-module').value;
    console.log(module_id);
    chrome.tabs.getSelected(null,function(tab) {
        const url = tab.url;
        const arr = url.split(".");
        console.log(url.split("https://"))
        let extension = "";
        if(arr.length)
            extension = arr[arr.length-1];
        console.log(extension);
        if(extension=='pdf')
            addPdf(id, module_id, url);
        if(extension=='jpg'||extension=='jpeg'||extension=='png')
            addImage(id, module_id, url);
        if(extension=='mp4'||extension=='mov'||extension=='wmv')
            addVideo(id, module_id, url);
    });
})