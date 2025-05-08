import { useState } from "react";
import * as React from "react";
import {withAuthenticator} from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";
import HealthMonitor from './HealthMonitor'
import S2sChatBot from './s2s'

const App = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '40px', padding: '40px' }}>
      <HealthMonitor />
      <S2sChatBot />
    </div>
  );
}
export default App;
