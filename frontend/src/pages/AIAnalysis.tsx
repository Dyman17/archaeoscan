import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Brain, 
  Droplets, 
  Shield, 
  Gem,
  Activity,
  AlertTriangle,
  CheckCircle,
  Loader2
} from 'lucide-react';

interface AIAnalysis {
  water: {
    preservation: 'excellent' | 'good' | 'fair' | 'poor';
    reason: string;
    turbidity: number;
    temperature: number;
    ph: number;
  };
  material: {
    type: 'ceramic' | 'metal' | 'stone' | 'organic' | 'unknown';
    confidence: number;
    characteristics: string[];
  };
  timestamp: number;
}

export function AIAnalysis() {
  const [analysis, setAnalysis] = useState<AIAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeCurrentData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/ai/analyze');
      if (!response.ok) {
        throw new Error('Failed to get AI analysis');
      }
      
      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const getPreservationColor = (preservation: string) => {
    switch (preservation) {
      case 'excellent': return 'text-green-600 bg-green-50';
      case 'good': return 'text-blue-600 bg-blue-50';
      case 'fair': return 'text-yellow-600 bg-yellow-50';
      case 'poor': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getMaterialColor = (type: string) => {
    switch (type) {
      case 'ceramic': return 'bg-orange-100 text-orange-800';
      case 'metal': return 'bg-gray-100 text-gray-800';
      case 'stone': return 'bg-brown-100 text-brown-800';
      case 'organic': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Brain className="h-6 w-6" />
            AI Analysis
          </h1>
          <p className="text-muted-foreground">
            Real-time analysis of water conditions and material identification
          </p>
        </div>
        <Button 
          onClick={analyzeCurrentData}
          disabled={loading}
          className="flex items-center gap-2"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Activity className="h-4 w-4" />
          )}
          {loading ? 'Analyzing...' : 'Analyze Current Data'}
        </Button>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-600">
              <AlertTriangle className="h-5 w-5" />
              <span>{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {analysis && (
        <>
          {/* Water Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Droplets className="h-5 w-5 text-blue-600" />
                Water Analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Preservation</p>
                  <Badge className={getPreservationColor(analysis.water.preservation)}>
                    <Shield className="h-3 w-3 mr-1" />
                    {analysis.water.preservation}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Turbidity</p>
                  <p className="text-lg font-semibold">{analysis.water.turbidity} NTU</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Temperature</p>
                  <p className="text-lg font-semibold">{analysis.water.temperature}°C</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">pH Level</p>
                  <p className="text-lg font-semibold">{analysis.water.ph}</p>
                </div>
              </div>
              
              <div>
                <p className="text-sm text-muted-foreground mb-2">Analysis Reason</p>
                <p className="text-sm bg-blue-50 p-3 rounded-lg">{analysis.water.reason}</p>
              </div>
            </CardContent>
          </Card>

          {/* Material Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Gem className="h-5 w-5 text-purple-600" />
                Material Identification
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Material Type</p>
                  <Badge className={getMaterialColor(analysis.material.type)}>
                    {analysis.material.type}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Confidence</p>
                  <div className="flex items-center gap-2">
                    <Progress value={analysis.material.confidence * 100} className="flex-1" />
                    <span className={`text-sm font-medium ${getConfidenceColor(analysis.material.confidence)}`}>
                      {(analysis.material.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  <div className="flex items-center gap-1">
                    {analysis.material.confidence >= 0.8 ? (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    ) : (
                      <AlertTriangle className="h-4 w-4 text-yellow-600" />
                    )}
                    <span className="text-sm">
                      {analysis.material.confidence >= 0.8 ? 'High confidence' : 'Low confidence'}
                    </span>
                  </div>
                </div>
              </div>

              {analysis.material.characteristics.length > 0 && (
                <div>
                  <p className="text-sm text-muted-foreground mb-2">Characteristics</p>
                  <div className="flex flex-wrap gap-2">
                    {analysis.material.characteristics.map((char, index) => (
                      <Badge key={index} variant="outline">
                        {char}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Analysis Info */}
          <Card>
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground">
                <p>Last analysis: {new Date(analysis.timestamp * 1000).toLocaleString()}</p>
                <p className="mt-1">
                  Note: AI analysis is based on current sensor readings and historical patterns. 
                  Results should be verified by archaeological experts.
                </p>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {!analysis && !loading && (
        <Card>
          <CardContent className="pt-6 text-center">
            <Brain className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Analysis Available</h3>
            <p className="text-muted-foreground mb-4">
              Click "Analyze Current Data" to get AI-powered insights about water conditions 
              and material identification.
            </p>
            <Button onClick={analyzeCurrentData}>
              <Activity className="h-4 w-4 mr-2" />
              Start Analysis
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
