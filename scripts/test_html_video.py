#!/usr/bin/env python3
"""
Test script for html_to_video.py

Creates a simple HTML demo page and records it as video to verify the html_to_video functionality.
"""

import os
import tempfile
from html_to_video import create_video_from_html

def create_demo_html():
    """Create a demo HTML page with animations for testing"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>37degrees HTML Video Test</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 40px;
            }
            
            h1 {
                font-size: 3em;
                text-align: center;
                margin-bottom: 30px;
                animation: fadeInUp 2s ease-out;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            .card {
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 30px;
                margin: 20px 0;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
                animation: slideInLeft 1.5s ease-out;
                transition: transform 0.3s ease;
            }
            
            .card:hover {
                transform: translateY(-5px) scale(1.02);
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            
            .pulse {
                animation: pulse 2s infinite;
            }
            
            .floating {
                animation: floating 3s ease-in-out infinite;
            }
            
            .book-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 40px 0;
            }
            
            .book-item {
                background: rgba(255,255,255,0.15);
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                animation: bounceIn 2s ease-out;
                animation-delay: 0.5s;
                animation-fill-mode: both;
            }
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(50px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            @keyframes slideInLeft {
                from {
                    opacity: 0;
                    transform: translateX(-100px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            @keyframes pulse {
                0%, 100% {
                    transform: scale(1);
                }
                50% {
                    transform: scale(1.05);
                }
            }
            
            @keyframes floating {
                0%, 100% {
                    transform: translateY(0px);
                }
                50% {
                    transform: translateY(-20px);
                }
            }
            
            @keyframes bounceIn {
                0% {
                    opacity: 0;
                    transform: scale(0.3);
                }
                50% {
                    opacity: 1;
                    transform: scale(1.05);
                }
                70% {
                    transform: scale(0.9);
                }
                100% {
                    opacity: 1;
                    transform: scale(1);
                }
            }
            
            .progress-bar {
                width: 100%;
                height: 8px;
                background: rgba(255,255,255,0.3);
                border-radius: 4px;
                overflow: hidden;
                margin: 20px 0;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #00c9ff, #92fe9d);
                width: 0%;
                border-radius: 4px;
                animation: fillProgress 8s ease-in-out;
            }
            
            @keyframes fillProgress {
                0% { width: 0%; }
                100% { width: 100%; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="floating">📚 37degrees Video Test</h1>
            
            <div class="card pulse">
                <h2>AI-Powered Book Visualization</h2>
                <p>Transforming classic literature into engaging TikTok content for Polish youth through AI-generated scenes and automated video production.</p>
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
            </div>
            
            <div class="book-grid">
                <div class="book-item">
                    <h3>🎭 Hamlet</h3>
                    <p>Shakespeare's tragedy brought to life with AI-generated scenes</p>
                </div>
                <div class="book-item">
                    <h3>📖 Crime and Punishment</h3>
                    <p>Dostoyevsky's psychological drama visualized</p>
                </div>
                <div class="book-item">
                    <h3>⚔️ The Iliad</h3>
                    <p>Epic battles and heroic tales in cinematic style</p>
                </div>
            </div>
            
            <div class="card">
                <h2>🎥 Video Generation Pipeline</h2>
                <ul>
                    <li>📝 Scene generation with AI agents</li>
                    <li>🎨 Style application and visual enhancement</li>
                    <li>🖼️ Image generation using advanced AI</li>
                    <li>🎬 Video compilation with transitions</li>
                    <li>📱 TikTok-optimized vertical format</li>
                </ul>
            </div>
            
            <div class="card floating">
                <h2>✨ Features</h2>
                <p>This HTML to Video test demonstrates the capability to record web content, including CSS animations, transitions, and interactive elements.</p>
                <p><strong>Technology Stack:</strong> Playwright + Python + FFmpeg</p>
            </div>
        </div>
        
        <script>
            // Add some JavaScript animations
            setTimeout(() => {
                document.querySelectorAll('.card').forEach((card, index) => {
                    setTimeout(() => {
                        card.style.transform = 'translateY(-10px)';
                        setTimeout(() => {
                            card.style.transform = 'translateY(0)';
                        }, 300);
                    }, index * 500);
                });
            }, 3000);
            
            // Simulate loading progress
            setTimeout(() => {
                const progressBar = document.querySelector('.progress-fill');
                if (progressBar) {
                    progressBar.style.width = '100%';
                }
            }, 1000);
        </script>
    </body>
    </html>
    """
    return html_content

def test_html_video():
    """Test the HTML to video functionality"""
    print("🧪 Testing HTML to Video conversion...")
    
    # Create temporary HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(create_demo_html())
        temp_html_path = f.name
    
    try:
        # Test video creation
        output_path = "test_output.webm"
        
        # Custom interactions for more interesting demo
        interactions = [
            {"type": "wait", "duration": 2000},
            {"type": "scroll", "y": 300},
            {"type": "wait", "duration": 2000},
            {"type": "hover", "selector": ".card:first-child"},
            {"type": "wait", "duration": 1500},
            {"type": "scroll", "y": 600},
            {"type": "wait", "duration": 2000},
            {"type": "hover", "selector": ".book-item:nth-child(2)"},
            {"type": "wait", "duration": 1500},
            {"type": "scroll", "y": 1000},
            {"type": "wait", "duration": 2000},
            {"type": "scroll", "y": 0},
            {"type": "wait", "duration": 1000}
        ]
        
        success = create_video_from_html(
            html_path=temp_html_path,
            output_path=output_path,
            duration=15,
            width=1024,
            height=1536,
            headless=True,
            interactions=interactions
        )
        
        if success:
            print("✅ Test completed successfully!")
            print(f"📁 Video saved as: {output_path}")
            return True
        else:
            print("❌ Test failed!")
            return False
            
    finally:
        # Cleanup
        if os.path.exists(temp_html_path):
            os.unlink(temp_html_path)

if __name__ == "__main__":
    test_html_video()