// Type declarations for vis-timeline
declare module 'vis-timeline/standalone' {
  export interface TimelineOptions {
    height?: string | number;
    groupOrder?: string | ((a: any, b: any) => number);
    editable?: boolean;
    showCurrentTime?: boolean;
    margin?: {
      item?: number;
      axis?: number;
    };
    orientation?: string;
    zoomMin?: number;
    zoomMax?: number;
    stack?: boolean;
    tooltip?: {
      followMouse?: boolean;
      overflowMethod?: 'flip' | 'cap' | 'none';
    };
  }

  export interface TimelineItem {
    id: string | number;
    content: string;
    start: Date | string;
    end?: Date | string;
    group?: string | number;
    type?: string;
    title?: string;
    className?: string;
  }

  export interface TimelineGroup {
    id: string | number;
    content: string;
    className?: string;
  }

  export class Timeline {
    constructor(container: HTMLElement, items: DataSet | TimelineItem[], groups?: DataSet | TimelineGroup[], options?: TimelineOptions);
    on(event: string, callback: (properties: any) => void): void;
    off(event: string, callback: (properties: any) => void): void;
    destroy(): void;
    fit(): void;
    zoomIn(percentage: number): void;
    zoomOut(percentage: number): void;
    setOptions(options: TimelineOptions): void;
  }

  export class DataSet {
    constructor(items?: any[]);
    add(items: any[] | any): void;
    update(items: any[] | any): void;
    remove(ids: string[] | string): void;
    clear(): void;
    get(options?: any): any[];
    getIds(): string[];
  }
}

// Type declarations for Material-UI if missing
declare module '@mui/material' {
  export * from '@mui/material/index';
}

declare module '@mui/material/styles' {
  export * from '@mui/material/styles/index';
}

declare module '@mui/icons-material' {
  export * from '@mui/icons-material/index';
}

// Global JSX namespace
declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
    div: React.DetailedHTMLProps<React.HTMLAttributes<HTMLDivElement>, HTMLDivElement>;
    span: React.DetailedHTMLProps<React.HTMLAttributes<HTMLSpanElement>, HTMLSpanElement>;
    strong: React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
    button: React.DetailedHTMLProps<React.ButtonHTMLAttributes<HTMLButtonElement>, HTMLButtonElement>;
    input: React.DetailedHTMLProps<React.InputHTMLAttributes<HTMLInputElement>, HTMLInputElement>;
    p: React.DetailedHTMLProps<React.HTMLAttributes<HTMLParagraphElement>, HTMLParagraphElement>;
    h1: React.DetailedHTMLProps<React.HTMLAttributes<HTMLHeadingElement>, HTMLHeadingElement>;
    h2: React.DetailedHTMLProps<React.HTMLAttributes<HTMLHeadingElement>, HTMLHeadingElement>;
    h3: React.DetailedHTMLProps<React.HTMLAttributes<HTMLHeadingElement>, HTMLHeadingElement>;
    h4: React.DetailedHTMLProps<React.HTMLAttributes<HTMLHeadingElement>, HTMLHeadingElement>;
    h5: React.DetailedHTMLProps<React.HTMLAttributes<HTMLHeadingElement>, HTMLHeadingElement>;
    h6: React.DetailedHTMLProps<React.HTMLAttributes<HTMLHeadingElement>, HTMLHeadingElement>;
    ul: React.DetailedHTMLProps<React.HTMLAttributes<HTMLUListElement>, HTMLUListElement>;
    ol: React.DetailedHTMLProps<React.OlHTMLAttributes<HTMLOListElement>, HTMLOListElement>;
    li: React.DetailedHTMLProps<React.LiHTMLAttributes<HTMLLIElement>, HTMLLIElement>;
  }
}
