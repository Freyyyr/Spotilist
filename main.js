const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const net = require('net');

let mainWindow;
let pythonProcess;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 720,
        title: "Spotilist",
        show: false,
        webPreferences: {
            nodeIntegration: false
        }
    });

    const appUrl = 'http://127.0.0.1:8501';

    const checkServer = () => {
        const client = new net.Socket();

        client.connect(8501, '127.0.0.1', () => {
            client.destroy();
            console.log("Streamlit ready ! Loading...");
            mainWindow.loadURL(appUrl);
            mainWindow.show();
        });

        client.on('error', (err) => {
            client.destroy();
            setTimeout(checkServer, 500);
        });
    };

    checkServer();

    mainWindow.on('closed', function () {
        mainWindow = null;
    });
}
function startPython() {
    let scriptPath;

    if (!app.isPackaged) {
        console.log("Mode Dev: Lancez le backend python manuellement !");
        return;
    }

    if (process.platform === 'win32') {
        scriptPath = path.join(
            process.resourcesPath,
            'spotilist_backend.exe'
        );
    }
    else if (process.platform === 'darwin') {
        scriptPath = path.join(
            process.resourcesPath,
            'spotilist_backend'
        );
    }
    else {
        scriptPath = path.join(
            process.resourcesPath,
            'spotilist_backend'
        );
    }

    console.log("Looking for Python executable at:", scriptPath);

    const userDataPath = app.getPath('userData');

    pythonProcess = spawn(scriptPath, [], {
        cwd: userDataPath,
        env: {
            ...process.env,
            DYLD_LIBRARY_PATH: process.resourcesPath,
            STREAMLIT_SERVER_PORT: '8501',
            STREAMLIT_SERVER_ADDRESS: '127.0.0.1'
        }
    });

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python Error: ${data}`);
    });

    pythonProcess.on('exit', (code) => {
        console.log(`Python process exited with code ${code}`);
    });
}


app.on('ready', () => {
    if (app.isPackaged) startPython();
    createWindow();
});

app.on('will-quit', () => {
    if (pythonProcess) pythonProcess.kill();
});