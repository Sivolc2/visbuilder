declare module '@deck.gl/react' {
  import { Component } from 'react';
  export default class DeckGL extends Component<any> {}
}

declare module '@deck.gl/core' {
  export interface ViewState {
    longitude: number;
    latitude: number;
    zoom: number;
    pitch: number;
    bearing: number;
  }
}

declare module '@deck.gl/layers' {
  export class LineLayer {
    constructor(props: any);
  }
  export class PolygonLayer {
    constructor(props: any);
  }
  export class ScatterplotLayer {
    constructor(props: any);
  }
}

declare module '@deck.gl/aggregation-layers' {
  export class HexagonLayer {
    constructor(props: any);
  }
  export class HeatmapLayer {
    constructor(props: any);
  }
}

declare module '@deck.gl/geo-layers' {
  export class H3HexagonLayer {
    constructor(props: any);
  }
} 