import { useState } from 'react';

interface FileTreeProps {
  color: string;
}

interface TreeNode {
  name: string;
  type: 'dir' | 'file';
  children?: TreeNode[];
  expanded?: boolean;
  size?: string;
  perms?: string;
}

const INITIAL_TREE: TreeNode[] = [
  {
    name: '/',
    type: 'dir',
    expanded: true,
    perms: 'drwxr-xr-x',
    children: [
      {
        name: 'bin/', type: 'dir', perms: 'drwxr-xr-x',
        children: [
          { name: 'sh', type: 'file', size: '122K', perms: '-rwxr-xr-x' },
          { name: 'ls', type: 'file', size: '72K', perms: '-rwxr-xr-x' },
          { name: 'cat', type: 'file', size: '44K', perms: '-rwxr-xr-x' },
        ]
      },
      {
        name: 'data/', type: 'dir', perms: 'drwx------',
        children: [
          { name: 'app/', type: 'dir', perms: 'drwxrwx--x', children: [] },
          { name: 'local/', type: 'dir', perms: 'drwxrwx--x', children: [] },
          { name: 'media/', type: 'dir', perms: 'drwxrwx--x', children: [] },
        ]
      },
      {
        name: 'dev/', type: 'dir', perms: 'drwxr-xr-x',
        children: [
          { name: 'null', type: 'file', size: '0', perms: 'crw-rw-rw-' },
          { name: 'random', type: 'file', size: '0', perms: 'crw-rw-rw-' },
          { name: 'tty0', type: 'file', size: '0', perms: 'crw--w----' },
        ]
      },
      {
        name: 'etc/', type: 'dir', perms: 'drwxr-xr-x',
        children: [
          { name: 'passwd', type: 'file', size: '1.4K', perms: '-rw-r--r--' },
          { name: 'shadow', type: 'file', size: '892', perms: '-rw------- 🔒' },
          { name: 'hosts', type: 'file', size: '174', perms: '-rw-r--r--' },
          { name: 'fstab', type: 'file', size: '512', perms: '-rw-r--r--' },
        ]
      },
      {
        name: 'proc/', type: 'dir', perms: 'dr-xr-xr-x',
        children: [
          { name: 'cpuinfo', type: 'file', size: '0', perms: '-r--r--r--' },
          { name: 'meminfo', type: 'file', size: '0', perms: '-r--r--r--' },
          { name: 'net/', type: 'dir', perms: 'dr-xr-xr-x', children: [] },
        ]
      },
      {
        name: 'sys/', type: 'dir', perms: 'dr-xr-xr-x',
        children: [
          { name: 'kernel/', type: 'dir', perms: 'dr-xr-xr-x', children: [] },
          { name: 'fs/', type: 'dir', perms: 'dr-xr-xr-x', children: [] },
        ]
      },
      {
        name: 'system/', type: 'dir', perms: 'drwxr-xr-x',
        children: [
          { name: 'app/', type: 'dir', perms: 'drwxr-xr-x', children: [] },
          { name: 'lib/', type: 'dir', perms: 'drwxr-xr-x', children: [] },
          { name: 'framework/', type: 'dir', perms: 'drwxr-xr-x', children: [] },
        ]
      },
      { name: 'tmp/', type: 'dir', perms: 'drwxrwxrwt', children: [] },
    ]
  }
];

function TreeNodeView({
  node,
  depth,
  prefix,
  isLast,
  color,
  onToggle,
  path,
}: {
  node: TreeNode;
  depth: number;
  prefix: string;
  isLast: boolean;
  color: string;
  onToggle: (path: number[]) => void;
  path: number[];
}) {
  const connector = isLast ? '└── ' : '├── ';
  const childPrefix = prefix + (isLast ? '    ' : '│   ');
  const isDir = node.type === 'dir';
  const dim = `${color}70`;
  const faint = `${color}40`;

  return (
    <div>
      <div
        className="flex items-center gap-1 hover:bg-white/5 rounded cursor-pointer leading-tight py-px"
        onClick={() => isDir && node.children ? onToggle(path) : undefined}
        style={{ paddingLeft: depth === 0 ? 0 : undefined }}
      >
        <span style={{ color: faint, fontFamily: 'monospace', whiteSpace: 'pre' }}>{prefix}{connector}</span>
        {isDir ? (
          <span style={{ color }} className="select-none">
            {node.expanded ? '▾ ' : '▸ '}{node.name}
          </span>
        ) : (
          <span style={{ color: dim }} className="select-none">{node.name}</span>
        )}
        {node.size && <span style={{ color: faint }} className="ml-auto text-xs">{node.size}</span>}
      </div>
      {isDir && node.expanded && node.children && node.children.map((child, i) => (
        <TreeNodeView
          key={child.name}
          node={child}
          depth={depth + 1}
          prefix={childPrefix}
          isLast={i === (node.children!.length - 1)}
          color={color}
          onToggle={onToggle}
          path={[...path, i]}
        />
      ))}
    </div>
  );
}

function toggleNodeAt(tree: TreeNode[], path: number[]): TreeNode[] {
  if (path.length === 0) return tree;
  const [head, ...rest] = path;
  return tree.map((node, i) => {
    if (i !== head) return node;
    if (rest.length === 0) return { ...node, expanded: !node.expanded };
    return { ...node, children: node.children ? toggleNodeAt(node.children, rest) : node.children };
  });
}

export function FileTree({ color }: FileTreeProps) {
  const [tree, setTree] = useState<TreeNode[]>(INITIAL_TREE);
  const dim = `${color}80`;

  const handleToggle = (pathFromRoot: number[]) => {
    setTree(prev => {
      // The root node is at index 0 of tree, its children start at path offset
      // pathFromRoot is relative to root's children array
      const [rootIdx, ...childPath] = pathFromRoot;
      if (childPath.length === 0) {
        return prev.map((n, i) => i === rootIdx ? { ...n, expanded: !n.expanded } : n);
      }
      return prev.map((n, i) => {
        if (i !== rootIdx) return n;
        return { ...n, children: n.children ? toggleNodeAt(n.children, childPath) : n.children };
      });
    });
  };

  const faint = `${color}40`;

  return (
    <div
      className="border rounded overflow-hidden mb-4"
      style={{
        borderColor: `${color}40`,
        backgroundColor: `${color}05`,
        boxShadow: `0 0 12px ${color}20`,
        maxHeight: '220px',
      }}
    >
      <div
        className="font-mono text-xs px-3 py-1 border-b tracking-widest"
        style={{ color, borderColor: `${color}30`, backgroundColor: `${color}10` }}
      >
        ▸ FILESYSTEM ── /root ─────────────────────
      </div>
      <div
        className="overflow-y-auto font-mono px-3 py-2"
        style={{ color: dim, fontSize: '0.7rem', lineHeight: '1.6', maxHeight: '180px' }}
      >
        {/* Root node itself */}
        <div className="flex gap-1 items-center mb-0.5">
          <span style={{ color }} className="font-bold">{tree[0].expanded ? '▾' : '▸'} {tree[0].name}</span>
          <span style={{ color: faint }} className="text-xs ml-1">{tree[0].perms}</span>
        </div>
        {tree[0].expanded && tree[0].children?.map((child, i) => (
          <TreeNodeView
            key={child.name}
            node={child}
            depth={1}
            prefix=""
            isLast={i === (tree[0].children!.length - 1)}
            color={color}
            onToggle={(subPath) => handleToggle([0, i, ...subPath])}
            path={[]}
          />
        ))}
      </div>
    </div>
  );
}
