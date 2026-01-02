const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 720,
        title: "Spotilist",
        icon: path.join(__dirname, 'icon.png'),
        webPreferences: {
            nodeIntegration: false
        }
    });

    setTimeout(() => {
        mainWindow.loadURL('http://localhost:8501');
    }, 2000);

    mainWindow.on('closed', function () {
        mainWindow = null;
    });
}

function startPython() {
    let scriptPath;

    if (app.isPackaged) {
        let executableName = 'spotilist_backend';

        if (process.platform === 'win32') {
            executableName += '.exe';
        }

        scriptPath = path.join(process.resourcesPath, executableName);
    } else {
        console.log("Mode Dev: Lancez le backend python manuellement !");
        return;
    }

    const userDataPath = app.getPath('userData');

    pythonProcess = spawn(scriptPath, [], {
        cwd: userDataPath
    });

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python Error: ${data}`);
    });
}

app.on('ready', () => {
    if (app.isPackaged) startPython();
    createWindow();
});

app.on('will-quit', () => {
    if (pythonProcess) pythonProcess.kill();
});