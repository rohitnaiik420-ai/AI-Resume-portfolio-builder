import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_health():
    res = client.get('/health')
    assert res.status_code == 200
    data = res.json()
    assert data.get('status') == 'ok'
    print('[PASS] Health check passed: status=ok')

def test_ats_test_endpoint():
    payload = {
        'job_description': 'Looking for a Senior Python Developer with FastAPI, PostgreSQL, Docker, AWS, React, Kubernetes experience. Must have 5+ years experience and Bachelor degree in Computer Science.',
        'resume_text': 'Rohit Naik - Python Developer with experience in FastAPI, PostgreSQL, Docker, Git. Built REST APIs and responsive web apps.',
        'resume': {
            'p': {
                'name': 'Rohit Naik',
                'title': 'Senior Python Developer',
                'email': 'rohit@example.com',
                'phone': '+91 9876543210',
                'linkedin': 'linkedin.com/in/rohitnaik',
                'summary': 'Senior Python engineer with 5 years experience.'
            },
            'sk': ['Python', 'FastAPI', 'PostgreSQL', 'Docker', 'Git'],
            'exp': [{
                'title': 'Senior Developer',
                'co': 'Tech Corp',
                'start': '2021',
                'end': 'Present',
                'body': 'Architected microservices that improved performance by 40%.'
            }],
            'edu': [{
                'degree': 'B.Tech Computer Science',
                'inst': 'National University'
            }]
        }
    }
    res = client.post('/api/ats-test', json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert 'estimated_ats_score' in data
    assert 'scoring_breakdown' in data
    assert 'matched_keywords' in data
    assert 'missing_keywords' in data
    assert 'formatting_hazards' in data
    assert 'recommendations' in data
    assert 0 <= data['estimated_ats_score'] <= 100
    print('[PASS] ATS Test Endpoint: Score = ' + str(data['estimated_ats_score']) + ', Matched = ' + str(len(data['matched_keywords'])) + ', Missing = ' + str(len(data['missing_keywords'])))

def test_score_endpoint():
    payload = {
        'p': {
            'name': 'Rohit Naik',
            'title': 'Full Stack Engineer',
            'email': 'rohit@example.com',
            'phone': '+91 9876543210',
            'summary': 'Experienced developer with 4+ years building high scale apps.'
        },
        'sk': ['Python', 'React', 'TypeScript', 'FastAPI', 'PostgreSQL'],
        'exp': [{
            'title': 'Full Stack Engineer',
            'co': 'DevStudio',
            'start': '2022',
            'end': 'Present',
            'body': 'Led development of enterprise microservices architecture.'
        }],
        'edu': [{
            'degree': 'B.Tech in Computer Science',
            'inst': 'Tech University'
        }],
        'proj': [{
            'name': 'AI Resume Builder',
            'tech': 'FastAPI, HTML5',
            'body': 'Built AI Resume Builder with 10k users'
        }]
    }
    res = client.post('/api/score', json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert 'overall' in data
    print('[PASS] Resume Score Endpoint: Score = ' + str(data.get('overall')))

if __name__ == '__main__':
    test_health()
    test_ats_test_endpoint()
    test_score_endpoint()
    print('ALL BACKEND TESTS PASSED SUCCESSFULLY!')
