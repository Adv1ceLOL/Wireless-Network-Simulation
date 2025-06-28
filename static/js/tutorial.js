// Tutorial and Help System for Wireless Network Simulator
class TutorialSystem {
    constructor() {
        this.tutorialSteps = [
            {
                title: "Welcome to the Wireless Sensor Network Simulator",
                text: "This simulator allows you to create and study wireless sensor networks. Get started by creating a network in the left panel, then use the simulation controls to observe the network's behavior over time."
            },
            {
                title: "Creating Your Network",
                text: "Start by configuring your network parameters. Set the number of nodes and area size, then click 'Create Network' to generate a random network topology."
            },
            {
                title: "Running the Simulation",
                text: "Use the Simulation Controls to adjust probabilities for events and step through the simulation. P(Request) controls how often nodes send requests, P(Fail) sets the chance of node failures, and P(New) determines if new nodes appear."
            },
            {
                title: "Analyzing Your Network",
                text: "Click on nodes to see detailed information. Check the statistics panel to track performance metrics. The Event Log shows you a chronological record of what's happening in your network."
            },
            {
                title: "Customizing the Topology",
                text: "Use the Topology Controls to manually add or remove links between nodes. This lets you test specific network configurations and observe their behavior."
            },
            {
                title: "Exporting Results",
                text: "When you've finished your simulation, use the Export & Reports panel to save your results as JSON data, generate a detailed report, or export the network visualization as an image."
            }
        ];
        
        this.currentStep = 0;
        this.tutorialEnabled = true;
        
        this.init();
    }
    
    init() {
        if (localStorage.getItem('tutorialDismissed') === 'true') {
            this.hideTutorial();
        }
        
        document.getElementById('dismissTutorial').addEventListener('click', () => {
            this.dismissTutorial();
        });
        
        document.getElementById('nextTutorialStep').addEventListener('click', () => {
            this.nextStep();
        });
        
        // Create Help button in header
        const connectionStatus = document.querySelector('.connection-status');
        const helpButton = document.createElement('button');
        helpButton.className = 'btn btn-small';
        helpButton.innerHTML = '❓ Help';
        helpButton.style.marginLeft = '10px';
        helpButton.addEventListener('click', () => this.showHelpModal());
        connectionStatus.appendChild(helpButton);
        
        // Add close event to help modal
        document.querySelector('#closeHelpModal').addEventListener('click', () => {
            document.getElementById('helpModal').style.display = 'none';
        });
        
        // Close modal when clicking on X
        document.querySelectorAll('.modal .close').forEach(closeBtn => {
            closeBtn.addEventListener('click', function() {
                this.closest('.modal').style.display = 'none';
            });
        });
        
        // Close modal when clicking outside
        window.addEventListener('click', (event) => {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = 'none';
            }
        });
    }
    
    showHelpModal() {
        document.getElementById('helpModal').style.display = 'block';
    }
    
    dismissTutorial() {
        localStorage.setItem('tutorialDismissed', 'true');
        this.hideTutorial();
    }
    
    hideTutorial() {
        const tutorialSection = document.getElementById('tutorialSection');
        tutorialSection.style.display = 'none';
        this.tutorialEnabled = false;
    }
    
    nextStep() {
        this.currentStep = (this.currentStep + 1) % this.tutorialSteps.length;
        this.updateTutorialContent();
    }
    
    updateTutorialContent() {
        const step = this.tutorialSteps[this.currentStep];
        const tutorialSection = document.getElementById('tutorialSection');
        const titleElement = tutorialSection.querySelector('h4');
        const textElement = tutorialSection.querySelector('.tutorial-text');
        
        titleElement.innerHTML = `<i class="fas fa-lightbulb"></i> ${step.title}`;
        textElement.textContent = step.text;
        
        // Update button text on last step
        const nextButton = document.getElementById('nextTutorialStep');
        if (this.currentStep === this.tutorialSteps.length - 1) {
            nextButton.textContent = "Start Over";
        } else {
            nextButton.textContent = "Next Tip";
        }
    }
    
    resetTutorial() {
        localStorage.removeItem('tutorialDismissed');
        document.getElementById('tutorialSection').style.display = 'block';
        this.currentStep = 0;
        this.tutorialEnabled = true;
        this.updateTutorialContent();
    }
}

// Initialize the tutorial system when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.tutorialSystem = new TutorialSystem();
});
