#ifndef GEOMETRY
#define GEOMETRY

#include <iostream>
#include <list>
#include <map>

class Vec3f
{
public:
    Vec3f();
    Vec3f(float x, float y);
    Vec3f(float x, float y, float z);
    
    Vec3f operator+(const Vec3f& rhs) const;
    Vec3f operator-(const Vec3f& rhs) const;
    Vec3f operator*(const float rhs) const;
    Vec3f operator/(const float rhs) const;
    
    bool operator<(const Vec3f& rhs) const;
    bool operator==(const Vec3f& rhs) const;
    bool operator!=(const Vec3f& rhs) const;
    
    Vec3f norm() const;
    float len() const;
    Vec3f rotate90() const;
    float dot(const Vec3f& rhs) const;
    
    friend std::ostream& operator<<(std::ostream& o, const Vec3f& v);

    float x, y, z;
};

std::ostream& operator<<(std::ostream& o, const Vec3f& v);

////////////////////////////////////////////////////////////////////////////////

typedef struct Triangle {
    Triangle(Vec3f v1, Vec3f v2, Vec3f v3);
    bool operator<(const Triangle& rhs) const;
        
    Vec3f v1, v2, v3;
} Triangle;

////////////////////////////////////////////////////////////////////////////////

typedef struct Edge {
    Edge(Vec3f v1, Vec3f v2);
    bool operator<(const Edge& rhs) const;
        
    Vec3f v1, v2;
} Edge;

////////////////////////////////////////////////////////////////////////////////

class Path : public std::list<Vec3f>
{
public:
    Path();
    Path(Vec3f v1, Vec3f v2);
    
    bool operator<(const Path& rhs) const;
};

////////////////////////////////////////////////////////////////////////////////

class PathSet
{
public:
    PathSet() : decimation_error(1) { /* Nothing to do here */ }
    PathSet(float de) : decimation_error(de) { /* Nothing to do here */ }
    
    PathSet& operator+=(Path p);
    
    std::list<Path>::iterator begin() { return paths.begin(); }
    std::list<Path>::iterator end()   { return paths.end(); }

    std::list<Path>::const_iterator begin() const { return paths.begin(); }
    std::list<Path>::const_iterator end() const   { return paths.end(); }
    
    std::list<Path> paths;
    float decimation_error;
    
private:
    std::map<Vec3f, std::list<Path>::iterator> beginnings;
    std::map<Vec3f, std::list<Path>::iterator> endings;
};
    
#endif