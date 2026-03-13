import React, { useRef, useEffect } from "react";
import { View, BackHandler, ActivityIndicator } from "react-native";
import { WebView } from "react-native-webview";

export default function App() {
  const webViewRef = useRef(null);

  const WEB_URL = "http://192.168.1.2:8000";

  const onBackPress = () => {
    if (webViewRef.current) {
      webViewRef.current.goBack();
      return true;
    }
    return false;
  };

  useEffect(() => {
    BackHandler.addEventListener("hardwareBackPress", onBackPress);
    return () =>
      BackHandler.removeEventListener("hardwareBackPress", onBackPress);
  }, []);

  return (
    <View style={{ flex: 1 }}>
      <WebView
        ref={webViewRef}
        source={{ uri: WEB_URL }}

        javaScriptEnabled={true}
        domStorageEnabled={true}
        originWhitelist={["*"]}

        mixedContentMode="always"

        thirdPartyCookiesEnabled={true}
        sharedCookiesEnabled={true}

        cacheEnabled={false}

        startInLoadingState={true}
        renderLoading={() => (
          <ActivityIndicator size="large" style={{ flex: 1 }} />
        )}

        allowsBackForwardNavigationGestures={true}
      />
    </View>
  );
}