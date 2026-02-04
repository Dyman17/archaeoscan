import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Database,
  Search,
  Filter,
  Download,
  MapPin,
  Calendar,
  Eye,
  ExternalLink,
  RefreshCw
} from 'lucide-react';

interface Artifact {
  id: number;
  location: [number, number];
  material: 'ceramic' | 'metal' | 'stone' | 'organic' | 'unknown';
  confidence: number;
  images: string[];
  date: string;
  depth: number;
  description: string;
  status: 'pending' | 'verified' | 'analyzed';
}

export function Artifacts() {
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterMaterial, setFilterMaterial] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const loadArtifacts = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/artifacts');
      if (response.ok) {
        const data = await response.json();
        setArtifacts(data);
      }
    } catch (error) {
      console.error('Failed to load artifacts:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadArtifacts();
  }, []);

  const filteredArtifacts = artifacts.filter(artifact => {
    const matchesSearch = artifact.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         artifact.material.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesMaterial = filterMaterial === 'all' || artifact.material === filterMaterial;
    const matchesStatus = filterStatus === 'all' || artifact.status === filterStatus;
    
    return matchesSearch && matchesMaterial && matchesStatus;
  });

  const exportData = async (format: 'csv' | 'json') => {
    try {
      const response = await fetch(`/api/artifacts/export?format=${format}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `artifacts.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const openOnMap = (artifact: Artifact) => {
    const [lat, lng] = artifact.location;
    window.open(`/map?lat=${lat}&lng=${lng}&artifact=${artifact.id}`, '_blank');
  };

  const getMaterialColor = (material: string) => {
    switch (material) {
      case 'ceramic': return 'bg-orange-100 text-orange-800';
      case 'metal': return 'bg-gray-100 text-gray-800';
      case 'stone': return 'bg-brown-100 text-brown-800';
      case 'organic': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'verified': return 'bg-green-100 text-green-800';
      case 'analyzed': return 'bg-blue-100 text-blue-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6 max-w-7xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Database className="h-6 w-6" />
            Artifacts Database
          </h1>
          <p className="text-muted-foreground">
            Manage and explore discovered archaeological artifacts
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={loadArtifacts} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button variant="outline" onClick={() => exportData('csv')}>
            <Download className="h-4 w-4 mr-2" />
            Export CSV
          </Button>
          <Button variant="outline" onClick={() => exportData('json')}>
            <Download className="h-4 w-4 mr-2" />
            Export JSON
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{artifacts.length}</div>
            <p className="text-sm text-muted-foreground">Total Artifacts</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">
              {artifacts.filter(a => a.status === 'verified').length}
            </div>
            <p className="text-sm text-muted-foreground">Verified</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">
              {artifacts.filter(a => a.confidence >= 0.8).length}
            </div>
            <p className="text-sm text-muted-foreground">High Confidence</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">
              {new Set(artifacts.map(a => a.material)).size}
            </div>
            <p className="text-sm text-muted-foreground">Material Types</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <Label htmlFor="search">Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="Search artifacts..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="material">Material</Label>
              <Select value={filterMaterial} onValueChange={setFilterMaterial}>
                <SelectTrigger id="material">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Materials</SelectItem>
                  <SelectItem value="ceramic">Ceramic</SelectItem>
                  <SelectItem value="metal">Metal</SelectItem>
                  <SelectItem value="stone">Stone</SelectItem>
                  <SelectItem value="organic">Organic</SelectItem>
                  <SelectItem value="unknown">Unknown</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="status">Status</Label>
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger id="status">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="analyzed">Analyzed</SelectItem>
                  <SelectItem value="verified">Verified</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end">
              <Button 
                variant="outline" 
                onClick={() => {
                  setSearchTerm('');
                  setFilterMaterial('all');
                  setFilterStatus('all');
                }}
              >
                Clear Filters
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Artifacts Table */}
      <Card>
        <CardHeader>
          <CardTitle>Artifacts ({filteredArtifacts.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading artifacts...</div>
          ) : filteredArtifacts.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No artifacts found matching your filters.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Material</TableHead>
                    <TableHead>Confidence</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Depth</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredArtifacts.map((artifact) => (
                    <TableRow key={artifact.id}>
                      <TableCell className="font-medium">#{artifact.id}</TableCell>
                      <TableCell>
                        <Badge className={getMaterialColor(artifact.material)}>
                          {artifact.material}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className={getConfidenceColor(artifact.confidence)}>
                          {(artifact.confidence * 100).toFixed(1)}%
                        </span>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          <span className="text-sm">
                            {artifact.location[0].toFixed(4)}, {artifact.location[1].toFixed(4)}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>{artifact.depth}m</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          <span className="text-sm">{artifact.date}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(artifact.status)}>
                          {artifact.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => openOnMap(artifact)}
                          >
                            <MapPin className="h-3 w-3 mr-1" />
                            Map
                          </Button>
                          <Button size="sm" variant="outline">
                            <Eye className="h-3 w-3 mr-1" />
                            View
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
