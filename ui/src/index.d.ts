export {};

interface IState {
  authenticated: boolean;
}

declare global {
  interface Window {
    SETTINGS: any;
    STATE: IState;
  }
}
