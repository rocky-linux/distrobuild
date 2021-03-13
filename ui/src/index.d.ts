export {};

interface IState {
  authenticated: boolean;
  fullName: string;
}

declare global {
  interface Window {
    SETTINGS: any;
    STATE: IState;
  }
}
