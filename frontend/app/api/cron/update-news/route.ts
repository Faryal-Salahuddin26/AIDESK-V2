import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  // Verify cron secret (security)
  const authHeader = request.headers.get('authorization');
  const cronSecret = process.env.CRON_SECRET;
  
  if (cronSecret && authHeader !== `Bearer ${cronSecret}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  try {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL;
    
    if (!backendUrl) {
      throw new Error('NEXT_PUBLIC_API_URL not configured');
    }
    
    // Trigger backend to process news (backend scheduler handles this)
    // This endpoint can trigger manual updates if needed
    
    // Alternatively, call the backend process endpoint directly
    const response = await fetch(`${backendUrl}/api/v1/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        topic: 'AI news latest',
        max_articles: 10,
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Backend request failed: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    // Revalidate Next.js pages
    const revalidateSecret = process.env.REVALIDATE_SECRET;
    if (revalidateSecret) {
      try {
        await fetch(`${process.env.NEXT_PUBLIC_SITE_URL}/api/revalidate?secret=${revalidateSecret}`, {
          method: 'POST',
        });
      } catch (error) {
        console.error('Revalidation error:', error);
      }
    }
    
    return NextResponse.json({
      success: true,
      message: `Processed ${data.count || 0} articles`,
      timestamp: new Date().toISOString(),
    });
  } catch (error: any) {
    console.error('Cron job error:', error);
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: error.message,
      },
      { status: 500 }
    );
  }
}

