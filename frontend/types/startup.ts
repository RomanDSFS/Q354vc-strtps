export interface Startup {
    id: string;
    name: string;
    description: string;
    stage: string[];
    industry: string[];
    region: string[];
    min_check: number;
  }
  
  export interface StartupScoreDetails {
    usp: number;
    market: number;
    business_model: number;
    team: number;
    finance: number;
  }
  