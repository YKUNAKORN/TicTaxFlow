import React from 'react';
import { Link } from 'react-router-dom';
import { Users, Target, Award } from 'lucide-react';
import logo from '../assets/logo-icon.png';

const AboutPage: React.FC = () => {
    return (
        <div className="min-h-screen bg-white">
            {/* Navbar */}
            <nav className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
                <div className="flex items-center gap-2">
                    <Link to="/">
                        <img src={logo} alt="Logo" className="h-10 w-auto" />
                    </Link>
                    <Link to="/" className="text-xl font-bold text-slate-900">TicTaxFlow</Link>
                </div>
                <div className="hidden md:flex items-center gap-8">
                    <Link to="/" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">Home</Link>
                    <Link to="/features" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">Features</Link>
                    <Link to="/about" className="text-sm font-medium text-slate-900 transition-colors">About</Link>
                </div>
                <div className="flex items-center gap-4">
                    <Link to="/signin" className="text-sm font-medium text-slate-600 hover:text-slate-900">Login</Link>
                    <Link to="/signup" className="px-4 py-2 bg-slate-900 text-white text-sm font-medium rounded-lg hover:bg-slate-800 transition-colors">
                        Get Started
                    </Link>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto px-6 py-12 lg:py-24 animate-fade-in-up">
                {/* Mission Header */}
                <div className="text-center mb-24 max-w-4xl mx-auto">
                    <h1 className="text-4xl lg:text-7xl font-bold text-slate-900 mb-8 tracking-tight">
                        Simplifying Taxes <br />
                        <span className="text-slate-400">for everyone.</span>
                    </h1>
                    <p className="text-slate-500 text-xl lg:text-2xl leading-relaxed font-light">
                        "We believe that managing personal income tax shouldn't be a headache. 
                        It should be <span className="text-slate-900 font-medium">accessible</span>, <span className="text-slate-900 font-medium">accurate</span>, and <span className="text-slate-900 font-medium">stress-free</span>."
                    </p>
                </div>

                {/* Values Section */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-12 mb-32 border-y border-slate-100 py-20">
                    <div className="text-center space-y-6 px-4">
                        <div className="h-20 w-20 bg-primary-50 rounded-3xl flex items-center justify-center mx-auto text-primary-600 shadow-sm rotate-3 hover:rotate-6 transition-transform">
                            <Target size={40} />
                        </div>
                        <div>
                            <h3 className="text-2xl font-bold text-slate-900 mb-3">Accuracy First</h3>
                            <p className="text-slate-500 leading-relaxed">
                                We constantly update our algorithms with the latest Revenue Department regulations to ensuring precise calculations.
                            </p>
                        </div>
                    </div>
                    <div className="text-center space-y-6 px-4 border-x border-slate-100">
                        <div className="h-20 w-20 bg-secondary-50 rounded-3xl flex items-center justify-center mx-auto text-secondary-600 shadow-sm -rotate-3 hover:-rotate-6 transition-transform">
                            <Users size={40} />
                        </div>
                        <div>
                            <h3 className="text-2xl font-bold text-slate-900 mb-3">User Centric</h3>
                            <p className="text-slate-500 leading-relaxed">
                                Designed for real people, not just accountants. Our interface is intuitive, clean, and easy to navigate.
                            </p>
                        </div>
                    </div>
                    <div className="text-center space-y-6 px-4">
                        <div className="h-20 w-20 bg-accent-50 rounded-3xl flex items-center justify-center mx-auto text-accent-600 shadow-sm rotate-3 hover:rotate-6 transition-transform">
                            <Award size={40} />
                        </div>
                        <div>
                            <h3 className="text-2xl font-bold text-slate-900 mb-3">Innovation</h3>
                            <p className="text-slate-500 leading-relaxed">
                                Leveraging cutting-edge AI and OCR technology to automate tedious manual data entry tasks.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Story Section */}
                <div className="flex flex-col lg:flex-row gap-20 mb-32 items-center">
                    <div className="flex-1 space-y-8">
                        <div className="inline-block px-4 py-2 bg-slate-100 rounded-lg text-sm font-semibold text-slate-600 uppercase tracking-wider">
                            Our Story
                        </div>
                        <h2 className="text-4xl lg:text-5xl font-bold text-slate-900 leading-tight">
                            From Academic Project <br/> to Real Solution.
                        </h2>
                        <div className="space-y-6 text-lg text-slate-500 leading-relaxed">
                            <p>
                                TicTaxFlow started as an ambitious academic project with a simple goal: to solve the confusion around tax deduction allowances in Thailand. 
                            </p>
                            <p>
                                We realized that while the tax laws are public, understanding them and mapping daily expenses to the right categories is incredibly complex for the average person.
                            </p>
                            <p>
                                What began as a simple calculator has evolved into a comprehensive platform that helps users maximize their benefits legally and efficiently, powered by the latest advancements in Artificial Intelligence.
                            </p>
                        </div>
                    </div>
                    <div className="flex-1">
                        <div className="bg-slate-900 rounded-[2rem] p-12 text-white relative overflow-hidden shadow-2xl">
                             <div className="absolute top-0 right-0 p-32 bg-primary-600 rounded-full blur-[100px] opacity-20"></div>
                             <div className="absolute bottom-0 left-0 p-32 bg-secondary-600 rounded-full blur-[100px] opacity-20"></div>
                             
                             <div className="relative z-10 space-y-12">
                                <div className="border-l-2 border-slate-700 pl-8 space-y-2 relative">
                                    <div className="absolute -left-[9px] top-0 h-4 w-4 rounded-full bg-primary-500 ring-4 ring-slate-900"></div>
                                    <span className="text-primary-400 font-mono text-sm">Phase 1</span>
                                    <h4 className="text-xl font-bold">Concept & Research</h4>
                                    <p className="text-slate-400">Deep dive into Thai Revenue Code and user pain points.</p>
                                </div>
                                <div className="border-l-2 border-slate-700 pl-8 space-y-2 relative">
                                    <div className="absolute -left-[9px] top-0 h-4 w-4 rounded-full bg-secondary-500 ring-4 ring-slate-900"></div>
                                    <span className="text-secondary-400 font-mono text-sm">Phase 2</span>
                                    <h4 className="text-xl font-bold">AI Model Training</h4>
                                    <p className="text-slate-400">Developing custom OCR models for Thai receipt formats.</p>
                                </div>
                                <div className="border-l-2 border-slate-700 pl-8 space-y-2 relative">
                                    <div className="absolute -left-[9px] top-0 h-4 w-4 rounded-full bg-accent-500 ring-4 ring-slate-900"></div>
                                    <span className="text-accent-400 font-mono text-sm">Phase 3</span>
                                    <h4 className="text-xl font-bold">TicTaxFlow Beta</h4>
                                    <p className="text-slate-400">Launch of the full platform with automated categorization.</p>
                                </div>
                             </div>
                        </div>
                    </div>
                </div>

                {/* Tech Stack */}
                <div className="bg-slate-50 rounded-3xl p-12 lg:p-20 text-center">
                     <h2 className="text-3xl font-bold text-slate-900 mb-12">Powered by Modern Technology</h2>
                     <div className="flex flex-wrap justify-center gap-4 lg:gap-8 opacity-70 grayscale hover:grayscale-0 transition-all duration-500">
                        {['Python', 'FastAPI', 'React', 'TypeScript', 'Tailwind CSS', 'TensorFlow', 'PostgreSQL'].map((tech) => (
                            <div key={tech} className="px-6 py-3 bg-white rounded-xl shadow-sm border border-slate-200 text-lg font-semibold text-slate-700">
                                {tech}
                            </div>
                        ))}
                     </div>
                </div>
            </main>
        </div>
    );
};

export default AboutPage;
