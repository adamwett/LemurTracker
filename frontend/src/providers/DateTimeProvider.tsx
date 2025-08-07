import React, {createContext, useContext} from "react";
import { useGetHistory } from "../hooks/useGetHistory";

const DateTimeContext = createContext(null)

export const DateTimeProvider: React.FC<{children: React.ReactNode}> = ({children}) => {
    const {dateTime, setDateTime, currentVideoTime, setCurrentVideoTime, filteredData, data, loading} = useGetHistory()

    return (
        <DateTimeContext.Provider value={{dateTime, setDateTime, currentVideoTime, setCurrentVideoTime, filteredData, data, loading}}>
            {children}
        </DateTimeContext.Provider>
    )
}

export const useDateTimeProvider = () => {
    const context = useContext(DateTimeContext)
    if (!context) {
        throw new Error("useDateTimeProvider must be used within a DateTimeProvider")
    }
    return context
}