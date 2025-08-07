import { contextBridge, ipcRenderer } from 'electron';

// Define the API structure that will be exposed to the renderer process
export interface ElectronAPI {
    selectFolder: () => Promise<string | null>; // Declare the function signature
}

// Expose the API to the renderer process under the 'electronAPI' key
contextBridge.exposeInMainWorld('electronAPI', {
  // Map the 'selectFolder' function in the renderer API
  // to send an IPC message 'dialog:openDirectory' to the main process
  // and return the promise resolved by ipcMain.handle
  selectFolder: (): Promise<string | null> => ipcRenderer.invoke('dialog:openDirectory'), 
  getDirname: () => __dirname // Expose __dirname to the renderer process
});

// Optional: If you need to expose other things, add them here
// contextBridge.exposeInMainWorld('otherAPI', {
//   doSomethingElse: () => ipcRenderer.send('do-something'),
// });