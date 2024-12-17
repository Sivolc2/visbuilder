declare module '@deck.gl/react' {
  import { ViewState } from '@deck.gl/core';
  
  interface DeckGLProps {
    initialViewState: ViewState;
    controller: boolean;
    onViewStateChange: (params: { viewState: ViewState }) => void;
    children?: React.ReactNode;
    layers?: any[];
  }

  export default function DeckGL(props: DeckGLProps): JSX.Element;
}

declare module '@deck.gl/core' {
  export interface ViewState {
    longitude: number;
    latitude: number;
    zoom: number;
    pitch?: number;
    bearing?: number;
  }

  export type Position = [number, number] | [number, number, number];
}

declare module '@deck.gl/layers' {
  import { Position } from '@deck.gl/core';

  interface LayerProps {
    id: string;
    data: any[];
    pickable?: boolean;
    visible?: boolean;
    opacity?: number;
    getPosition?: (d: any) => Position;
    [key: string]: any;
  }

  export class Layer<P extends LayerProps = LayerProps> {
    constructor(props: P);
    clone(props: Partial<P>): this;
  }

  export class ScatterplotLayer extends Layer {
    constructor(props: LayerProps & {
      radiusScale?: number;
      radiusMinPixels?: number;
      radiusMaxPixels?: number;
      lineWidthMinPixels?: number;
      stroked?: boolean;
      filled?: boolean;
      getFillColor?: ((d: any) => number[]) | number[];
      getLineColor?: ((d: any) => number[]) | number[];
    });
  }
}

declare module '@deck.gl/geo-layers' {
  import { Layer, LayerProps } from '@deck.gl/layers';

  export class H3HexagonLayer extends Layer {
    constructor(props: LayerProps & {
      extruded?: boolean;
      elevationScale?: number;
      getHexagon?: (d: any) => string;
      getFillColor?: ((d: any) => number[]) | number[];
      getElevation?: ((d: any) => number) | number;
    });
  }
} 