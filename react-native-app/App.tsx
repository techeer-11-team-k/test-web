import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  View,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Keyboard,
} from 'react-native';

// API 설정 - 실제 서버 주소로 변경하세요
const API_BASE_URL = 'http://localhost:8000/api/v1/search';

interface Apartment {
  apt_id: string;
  apt_name: string;
  address: string;
  sigungu_name: string;
  dong_name: string;
  location: {
    lat: number;
    lng: number;
  } | null;
}

interface SearchResponse {
  success: boolean;
  data: {
    results: Apartment[];
  };
  meta: {
    query: string;
    count: number;
  };
}

export default function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState<Apartment[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [limit, setLimit] = useState(10);

  // 검색 실행
  const searchApartments = async () => {
    if (searchQuery.length < 2) {
      Alert.alert('알림', '검색어는 최소 2글자 이상 입력해주세요.');
      return;
    }

    Keyboard.dismiss();
    setLoading(true);
    setError(null);

    try {
      const url = `${API_BASE_URL}/apartments?q=${encodeURIComponent(searchQuery)}&limit=${limit}`;
      console.log('API 호출:', url);

      const response = await fetch(url);
      const data: SearchResponse = await response.json();

      if (data.success) {
        setResults(data.data.results);
      } else {
        setError('검색에 실패했습니다.');
        setResults([]);
      }
    } catch (err: any) {
      console.error('검색 오류:', err);
      setError(`연결 오류: ${err.message}`);
      setResults([]);
      
      Alert.alert(
        '연결 오류',
        '서버에 연결할 수 없습니다.\n\n서버가 실행 중인지 확인하세요:\nhttp://localhost:8000',
        [{ text: '확인' }]
      );
    } finally {
      setLoading(false);
    }
  };

  // 검색어 변경 시 자동 검색 (디바운싱)
  useEffect(() => {
    if (searchQuery.length >= 2) {
      const timer = setTimeout(() => {
        searchApartments();
      }, 500); // 500ms 디바운싱

      return () => clearTimeout(timer);
    } else {
      setResults([]);
    }
  }, [searchQuery]);

  const renderItem = ({ item }: { item: Apartment }) => (
    <TouchableOpacity style={styles.resultItem}>
      <Text style={styles.aptName}>{item.apt_name}</Text>
      <Text style={styles.address}>{item.address}</Text>
      <View style={styles.locationInfo}>
        <Text style={styles.locationText}>
          {item.sigungu_name} {item.dong_name}
        </Text>
        {item.location && (
          <Text style={styles.coords}>
            📍 {item.location.lat.toFixed(6)}, {item.location.lng.toFixed(6)}
          </Text>
        )}
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🏠 아파트 검색</Text>
        <Text style={styles.subtitle}>아파트명으로 검색하세요 (2글자 이상)</Text>
      </View>

      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="예: 래미안, 힐스테이트..."
          placeholderTextColor="#999"
          value={searchQuery}
          onChangeText={setSearchQuery}
          autoCapitalize="none"
          autoCorrect={false}
        />
        <TouchableOpacity
          style={[styles.searchButton, loading && styles.searchButtonDisabled]}
          onPress={searchApartments}
          disabled={loading || searchQuery.length < 2}
        >
          {loading ? (
            <ActivityIndicator color="#fff" size="small" />
          ) : (
            <Text style={styles.searchButtonText}>검색</Text>
          )}
        </TouchableOpacity>
      </View>

      <View style={styles.limitContainer}>
        <Text style={styles.limitLabel}>결과 개수:</Text>
        <View style={styles.limitButtons}>
          {[10, 20, 30, 50].map((num) => (
            <TouchableOpacity
              key={num}
              style={[
                styles.limitButton,
                limit === num && styles.limitButtonActive,
              ]}
              onPress={() => setLimit(num)}
            >
              <Text
                style={[
                  styles.limitButtonText,
                  limit === num && styles.limitButtonTextActive,
                ]}
              >
                {num}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>❌ {error}</Text>
        </View>
      )}

      {results.length > 0 && (
        <View style={styles.resultsHeader}>
          <Text style={styles.resultsCount}>
            검색 결과: {results.length}개
          </Text>
        </View>
      )}

      <FlatList
        data={results}
        renderItem={renderItem}
        keyExtractor={(item) => item.apt_id}
        style={styles.list}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          !loading && searchQuery.length >= 2 ? (
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyText}>검색 결과가 없습니다.</Text>
            </View>
          ) : null
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#667eea',
    padding: 20,
    paddingTop: 40,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.9,
  },
  searchContainer: {
    flexDirection: 'row',
    padding: 15,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  searchInput: {
    flex: 1,
    height: 45,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    paddingHorizontal: 15,
    fontSize: 16,
    marginRight: 10,
  },
  searchButton: {
    backgroundColor: '#667eea',
    paddingHorizontal: 20,
    height: 45,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    minWidth: 70,
  },
  searchButtonDisabled: {
    backgroundColor: '#ccc',
  },
  searchButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  limitContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  limitLabel: {
    fontSize: 14,
    color: '#666',
    marginRight: 10,
  },
  limitButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  limitButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    backgroundColor: '#f0f0f0',
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  limitButtonActive: {
    backgroundColor: '#667eea',
    borderColor: '#667eea',
  },
  limitButtonText: {
    fontSize: 14,
    color: '#666',
  },
  limitButtonTextActive: {
    color: '#fff',
    fontWeight: '600',
  },
  errorContainer: {
    backgroundColor: '#fee',
    padding: 15,
    margin: 15,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#fcc',
  },
  errorText: {
    color: '#c33',
    fontSize: 14,
  },
  resultsHeader: {
    padding: 15,
    paddingBottom: 10,
  },
  resultsCount: {
    fontSize: 14,
    color: '#666',
    fontWeight: '600',
  },
  list: {
    flex: 1,
  },
  listContent: {
    padding: 15,
    paddingTop: 0,
  },
  resultItem: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  aptName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  address: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  locationInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  locationText: {
    fontSize: 12,
    color: '#999',
  },
  coords: {
    fontSize: 11,
    color: '#667eea',
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
  },
});
