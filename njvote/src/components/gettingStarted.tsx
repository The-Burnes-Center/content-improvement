// GettingStarted.tsx
// This component provides a welcome screen and instructions for using MAX

const GettingStarted = () => {
  return (
    // Outer container that centers everything
    <div className="flex items-center justify-center w-full h-full p-8">
      {/* Main column layout */}
      
      <div className="flex flex-col items-center justify-center text-center space-y-8 max-w-2xl w-full ">
        
        {/* Heading */}
        <h1 className="text-4xl font-bold" style={{ color: 'rgb(4, 21, 39)' }}>👋 Welcome to MAX</h1>

        {/* Introductory paragraph */}
        <p className="text-lg" style={{ color: 'rgb(4, 21, 39)' }}>
          MAX (Machine Assistant for eXperience) helps you evaluate and improve your website’s content clarity, accessibility, and design.
        </p>

        {/* Steps container */}
        <div className="bg-gray-50 rounded-xl shadow-md px-10 py-8 w-full">
          
          {/* Subheading */}
          <h2 className="text-2xl font-semibold mb-6" style={{ color: 'rgb(4, 21, 39)' }}>🚀 Get Started in 4 Steps</h2>
          
          {/* Step-by-step instructions */}
          <div className="space-y-6 text-base text-gray-800 text-center" style={{ color: 'rgb(4, 21, 39)' }}>
            <p>🆕 <strong>Step 1:</strong> Click the <span className="font-mono text-sm">+</span> icon in the sidebar to create a new project.</p>
            <p>🌐 <strong>Step 2:</strong> Enter your project name and URL. MAX will begin analyzing automatically.</p>
            <p>📊 <strong>Step 3:</strong> Use the tabs above to explore insights into audience, content, design, and accessibility.</p>
            <p>🛠️ <strong>Step 4:</strong> Apply the suggestions to improve your site’s user experience.</p>
          </div>

        </div>
      </div>
    </div>
  );
};

export default GettingStarted;
