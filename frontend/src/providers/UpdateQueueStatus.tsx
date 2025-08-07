import React, {createContext, useContext, useState} from "react";

const UpdateQueueStatusContext = createContext(null)

export const UpdateQueueStatusProvider: React.FC<{children: React.ReactNode}> = ({children}) => {
    const [change, setChange] = useState(false);

    return (
        <UpdateQueueStatusContext.Provider value={{change, setChange}}>
            {children}
        </UpdateQueueStatusContext.Provider>
    )
}

export const useUpdateQueueStatusProvider = () => {
    const context = useContext(UpdateQueueStatusContext)
    if (!context) {
        throw new Error("useDateTimeProvider must be used within a DateTimeProvider")
    }
    return context
}