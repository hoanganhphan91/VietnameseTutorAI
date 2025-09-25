/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
        './src/components/**/*.{js,ts,jsx,tsx,mdx}',
        './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            animation: {
                'fade-in': 'fadeIn 0.6s ease-out forwards',
                'fade-in-up': 'fadeInUp 0.8s ease-out forwards',
                'spin-slow': 'spin 3s linear infinite',
                'float': 'float 6s ease-in-out infinite',
                'glow': 'glow 2s ease-in-out infinite alternate',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' }
                },
                fadeInUp: {
                    '0%': { 
                        opacity: '0',
                        transform: 'translateY(20px)'
                    },
                    '100%': { 
                        opacity: '1',
                        transform: 'translateY(0)'
                    }
                },
                float: {
                    '0%, 100%': { 
                        transform: 'translateY(0px) rotate(0deg)' 
                    },
                    '50%': { 
                        transform: 'translateY(-10px) rotate(5deg)' 
                    }
                },
                glow: {
                    '0%': { 
                        boxShadow: '0 0 20px rgba(59, 130, 246, 0.5)' 
                    },
                    '100%': { 
                        boxShadow: '0 0 30px rgba(147, 51, 234, 0.8)' 
                    }
                }
            }
        },
    },
    plugins: [],
}