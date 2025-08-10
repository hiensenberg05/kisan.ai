interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: (event: any) => void;
  onerror: (event: any) => void;
  onend: () => void;
  start: () => void;
  stop: () => void;
  abort: () => void;
}

declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition;
    webkitSpeechRecognition: new () => SpeechRecognition;
  }
}

export class SpeechToText {
  private recognition: SpeechRecognition | null = null;
  private isListening = false;
  private finalTranscript = '';
  private onResultCallback: ((text: string, isFinal: boolean) => void) | null = null;
  private onErrorCallback: ((error: string) => void) | null = null;
  private onEndCallback: (() => void) | null = null;
  
  constructor() {
    this.recognition = this.createRecognition();
  }

  private createRecognition(): SpeechRecognition | null {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.error('Speech recognition not supported in this browser');
      return null;
    }

    const recognition = new SpeechRecognition();
    
    // Configure for Indian English and Hinglish
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-IN';
    
    recognition.onresult = (event) => {
      let interimTranscript = '';
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        
        if (event.results[i].isFinal) {
          this.finalTranscript += transcript + ' ';
          this.onResultCallback?.(this.finalTranscript, true);
          this.finalTranscript = '';
        } else {
          interimTranscript += transcript;
          this.onResultCallback?.(interimTranscript, false);
        }
      }
    };
    
    recognition.onerror = (event: any) => {
      const errorMsg = event.error || 'Unknown speech recognition error';
      console.error('Speech recognition error:', errorMsg);
      if (this.onErrorCallback) {
        this.onErrorCallback(typeof errorMsg === 'string' ? errorMsg : 'Speech recognition failed');
      }
      this.stopListening();
    };
    
    recognition.onend = () => {
      if (this.isListening) {
        // Restart recognition if it was supposed to be running
        this.recognition?.start();
      } else if (this.onEndCallback) {
        this.onEndCallback();
      }
    };
    
    return recognition;
  }
  
  public startListening(
    onResult: (text: string, isFinal: boolean) => void,
    onError: (error: string) => void,
    onEnd: () => void
  ) {
    if (!this.recognition) {
      onError('Speech recognition not available');
      return;
    }
    
    this.onResultCallback = onResult;
    this.onErrorCallback = onError;
    this.onEndCallback = onEnd;
    
    try {
      this.recognition.start();
      this.isListening = true;
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      onError('Failed to start speech recognition');
    }
  }
  
  public stopListening() {
    if (this.recognition && this.isListening) {
      this.isListening = false;
      this.recognition.stop();
    }
  }
  
  public isSupported(): boolean {
    return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
  }
  
  public getSupportedLanguages(): string[] {
    // This is a simplified version. In a real app, you'd want to check the actual API
    return [
      'en-IN',  // Indian English
      'hi-IN',  // Hindi (India)
      'en-US',  // US English (fallback)
      'en-GB'   // UK English (fallback)
    ];
  }
}

export const speechToText = new SpeechToText();
