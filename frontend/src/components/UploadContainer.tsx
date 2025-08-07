import UploadView from "./UploadView";
import QueueStatusDisplay from "./QueueStatusDisplay";
import { UpdateQueueStatusProvider } from "../providers/UpdateQueueStatus";



const UploadContainer = () => {

    return (
        <UpdateQueueStatusProvider>
            <div className="content-wrapper">
                <div className="left-panel">
                    <UploadView/>
                </div>
                <div className="divider" />
                <div className="right-panel">
                    <QueueStatusDisplay/>
                </div>
            </div>
        </UpdateQueueStatusProvider>
    );
};

export default UploadContainer; 