import React from "react";

const TestComponent: React.FC = () => {
  return (
    <div style={{ padding: "20px", backgroundColor: "#f0f0f0", margin: "20px" }}>
      <h2>🧪 Operations Interface Test</h2>
      <p>If you can see this, the component is rendering correctly.</p>
      <div style={{ 
        padding: "10px", 
        backgroundColor: "#d4edda", 
        border: "1px solid #c3e6cb", 
        borderRadius: "5px",
        marginTop: "10px"
      }}>
        ✅ Component loaded successfully
      </div>
    </div>
  );
};

export default TestComponent;
