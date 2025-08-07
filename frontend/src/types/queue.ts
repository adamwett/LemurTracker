// src/types/queue.ts

// Represents the data for the currently processing item
export interface CurrentProcess {
    file_path: string;
    percent: number;
  }
  
  // Represents the response when the queue is processing items
  export interface QueueStatusProcessing {
    status: "processing";
    current_process: CurrentProcess;
    processes_on_deck: string[]; // Array of file paths
  }
  
  // Represents the response when the queue is not processing
  export interface QueueStatusNotProcessing {
    status: "not processing";
  }
  
  // Represents the response when an error occurs fetching the status
  export interface QueueStatusError {
      status: "error";
      message: string;
  }
  
  // A discriminated union type for all possible states fetched from the API
  export type QueueStatusResponse = QueueStatusProcessing | QueueStatusNotProcessing;
  
  // Represents the component's state, including loading and potential fetch errors
  export interface QueueComponentState {
      isLoading: boolean;
      error: string | null;
      data: QueueStatusResponse | null;
  }