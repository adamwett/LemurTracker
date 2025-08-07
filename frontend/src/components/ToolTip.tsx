import React, { useState } from 'react';
import { HelpCircle } from 'lucide-react';

interface TooltipProps {
    text: string;
}

const Tooltip: React.FC<TooltipProps> = ({ text }) => {
    const [showTooltip, setShowTooltip] = useState(false); 
    return (
        <div style={{ position: 'relative', display: 'inline-block', marginLeft: '408px', marginTop: '-32px' }}>
        <span
        style={{ cursor: 'help' }}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        >
        <HelpCircle size={20} color="#666" />
        </span>
        {showTooltip && (
        <div
            style={{
            position: 'absolute',
            bottom: '42px',
            transform: 'translateX(-50%)',
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            padding: '5px 10px',
            borderRadius: '4px',
            fontSize: '12px',
            whiteSpace: 'nowrap',
            zIndex: 100,
            minWidth: '200px',
            textAlign: 'center',
            }}
        >
            {text}
            <div
            style={{
                position: 'absolute',
                top: '100%',
                left: '53.25%',
                transform: 'translateX(-50%)',
                borderWidth: '5px',
                borderStyle: 'solid',
                borderColor: 'rgba(0, 0, 0, 0.8) transparent transparent transparent',
            }}
        />
        </div>
    )}
    </div>
);
};

export default Tooltip;