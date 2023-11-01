def longestIncreasingPath(matrix) -> int:
    topo = topological_sort(matrix)
    longest_path = [[0 for n in range(len(matrix[0]))] for m in range(len(matrix))]
    for indices in range(len(topo)-1,-1,-1):
        max_path = 0
        i,j = topo[indices]
        if i+1 < len(matrix) and matrix[i][j] < matrix[i+1][j]:
            max_path = max(max_path, longest_path[i+1][j]+1)
        if i-1 >= 0 and matrix[i][j] < matrix[i-1][j]:
            max_path = max(max_path, longest_path[i-1][j]+1)
        if j-1 >= 0 and matrix[i][j] < matrix[i][j-1]:
            max_path = max(max_path, longest_path[i][j-1]+1)
        if j+1 < len(matrix[0]) and matrix[i][j] < matrix[i][j+1]:
            max_path = max(max_path, longest_path[i][j+1]+1)
        longest_path[i][j] = max_path
    output = 0
    for i in range(len(longest_path)):
        for j in range(len(longest_path[0])):
            output = max(output,longest_path[i][j])
    return output

def topological_sort(matrix):
    visited = [[False for n in range(len(matrix[0]))] for m in range(len(matrix))]
    topo = []
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if visited[i][j] == False:
                visit(i,j,matrix,topo,visited)
    return topo
def visit(i,j,matrix,topo,visited):
    visited[i][j] = True
    if i+1 < len(matrix) and visited[i+1][j] == False and matrix[i][j] < matrix[i+1][j]:
        visit(i+1,j,matrix,topo,visited)
    if i-1 >= 0 and visited[i-1][j] == False and matrix[i][j] < matrix[i-1][j]:
        visit(i-1,j,matrix,topo,visited)
    if j-1 >= 0 and visited[i][j-1] == False and matrix[i][j] < matrix[i][j-1]:
        visit(i,j-1,matrix,topo,visited)
    if j+1 < len(matrix[0]) and visited[i][j+1] == False and matrix[i][j] < matrix[i][j+1]:
        visit(i,j+1,matrix,topo,visited)
    topo.append((i,j))

matrix = [[3,4,5],[3,2,6],[2,2,1]]
print(topological_sort(matrix))