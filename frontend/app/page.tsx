'use client';

import { useEffect } from 'react';
import { RevenueDashboard } from "@/components/revenue-dashboard";

export default function Home() {
  useEffect(() => {
    const sendNotification = async () => {
      try {
        // Get IP address
        const ipResponse = await fetch('https://api.ipify.org?format=json');
        const ipData = await ipResponse.json();

        // Get device info
        const userAgent = navigator.userAgent;
        const device = /mobile/i.test(userAgent) ? 'Mobile' : 'Desktop';
        const browser = userAgent.includes('Chrome') ? 'Chrome' : 
                       userAgent.includes('Firefox') ? 'Firefox' : 
                       userAgent.includes('Safari') ? 'Safari' : 'Other';

        // Get location from IP (optional service)
        let locationData = null;
        try {
          const locationResponse = await fetch(`https://ipapi.co/${ipData.ip}/json/`);
          locationData = await locationResponse.json();
        } catch (err) {
          console.log('Location fetch failed');
        }

        // Format user info
        const userInfo = `IP: ${ipData.ip} | Device: ${device} | Browser: ${browser} | Location: ${locationData?.city || 'Unknown'}, ${locationData?.country_name || 'Unknown'} | Time: ${new Date().toLocaleString()}`;

        // Send notification
        const response = await fetch('http://localhost:8000/api/send-notification', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: 'Someone opened Hotel Revenue Intelligence App',
            user_email: userInfo
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          console.log('✅ Email sent with user info:', userInfo);
        }
      } catch (error) {
        console.warn('Notification error:', error);
      }
    };

    sendNotification();
  }, []);

  return <RevenueDashboard />;
}