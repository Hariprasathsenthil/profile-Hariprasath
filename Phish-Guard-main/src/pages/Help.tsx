import React from 'react';
import { HelpCircle, Book, MessageCircle, Mail } from 'lucide-react';

export function Help() {
  return (
    <div className="bg-white py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl lg:text-center">
          <h2 className="text-base font-semibold leading-7 text-blue-600">Support Center</h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            How can we help you?
          </p>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Find answers to common questions, learn about phishing protection, or get in touch with our support team.
          </p>
        </div>
        
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-2">
            {/* FAQs */}
            <div className="flex flex-col bg-gray-50 rounded-lg p-8">
              <dt className="flex items-center gap-x-3 text-lg font-semibold leading-7 text-gray-900">
                <HelpCircle className="h-6 w-6 flex-none text-blue-600" />
                Frequently Asked Questions
              </dt>
              <dd className="mt-4 text-base leading-7 text-gray-600">
                <ul className="space-y-4">
                  <li>
                    <h3 className="font-medium text-gray-900">How does PhishGuard work?</h3>
                    <p className="mt-2">PhishGuard uses advanced algorithms to analyze URLs and emails for potential phishing threats, providing real-time protection for your organization.</p>
                  </li>
                  <li>
                    <h3 className="font-medium text-gray-900">What should I do if I detect a phishing attempt?</h3>
                    <p className="mt-2">Report it immediately through the dashboard and alert your IT team. PhishGuard will analyze the threat and update its detection patterns.</p>
                  </li>
                </ul>
              </dd>
            </div>

            {/* Documentation */}
            <div className="flex flex-col bg-gray-50 rounded-lg p-8">
              <dt className="flex items-center gap-x-3 text-lg font-semibold leading-7 text-gray-900">
                <Book className="h-6 w-6 flex-none text-blue-600" />
                Documentation
              </dt>
              <dd className="mt-4 text-base leading-7 text-gray-600">
                <ul className="space-y-4">
                  <li>
                    <a href="#" className="text-blue-600 hover:text-blue-500">Getting Started Guide</a>
                  </li>
                  <li>
                    <a href="#" className="text-blue-600 hover:text-blue-500">API Documentation</a>
                  </li>
                  <li>
                    <a href="#" className="text-blue-600 hover:text-blue-500">Best Practices</a>
                  </li>
                </ul>
              </dd>
            </div>

            {/* Contact Support */}
            <div className="flex flex-col bg-gray-50 rounded-lg p-8">
              <dt className="flex items-center gap-x-3 text-lg font-semibold leading-7 text-gray-900">
                <MessageCircle className="h-6 w-6 flex-none text-blue-600" />
                Live Chat Support
              </dt>
              <dd className="mt-4 text-base leading-7 text-gray-600">
                <p>Our support team is available 24/7 to help you with any questions or concerns.</p>
                <button className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                  Start Chat
                </button>
              </dd>
            </div>

            {/* Email Support */}
            <div className="flex flex-col bg-gray-50 rounded-lg p-8">
              <dt className="flex items-center gap-x-3 text-lg font-semibold leading-7 text-gray-900">
                <Mail className="h-6 w-6 flex-none text-blue-600" />
                Email Support
              </dt>
              <dd className="mt-4 text-base leading-7 text-gray-600">
                <p>For non-urgent inquiries, reach out to our support team via email.</p>
                <a href="mailto:support@phishguard.com" className="mt-4 inline-flex items-center text-blue-600 hover:text-blue-500">
                  support@phishguard.com
                </a>
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
}