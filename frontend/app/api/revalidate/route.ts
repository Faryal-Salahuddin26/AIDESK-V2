import { NextResponse } from 'next/server';
import { revalidatePath } from 'next/cache';

export async function POST(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const secret = searchParams.get('secret');
    
    // Verify secret
    if (secret !== process.env.REVALIDATE_SECRET) {
      return NextResponse.json({ error: 'Invalid secret' }, { status: 401 });
    }
    
    // Revalidate homepage
    revalidatePath('/');
    
    // Revalidate news pages
    revalidatePath('/news');
    
    return NextResponse.json({ 
      revalidated: true,
      timestamp: new Date().toISOString(),
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: 'Error revalidating', message: error.message },
      { status: 500 }
    );
  }
}

