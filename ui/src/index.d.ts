export {};

interface IState {
  authenticated: boolean;
  full_name: string;
}

declare global {
  interface Window {
    SETTINGS: any;
    STATE: IState;
  }
}
